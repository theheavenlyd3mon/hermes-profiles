"""Reference launcher for the SAM3 segmentation server behind the `segmentation` tool.

The `segmentation` MCP tool is a thin client: it POSTs an image + text prompt to
`{SAM3_SERVER_URL}/segment` and renders the returned masks. This script IS that
server — a multi-GPU SAM3 HTTP endpoint. Stand it up, point `SAM3_SERVER_URL` at
it, and `segmentation` works.

Prerequisites (this script does NOT install SAM3 — it only serves it):
  1. The `sam3` package importable (provides `sam3.model_builder`,
     `sam3.model.sam3_image_processor`) + its deps (torch with CUDA, etc.).
  2. Model checkpoint      → <sam3-root>/checkpoints/sam3.pt
     BPE vocab             → <sam3-root>/sam3/assets/bpe_simple_vocab_16e6.txt.gz
     Override either path with --checkpoint / --bpe (or SAM3_CHECKPOINT / SAM3_BPE_PATH).
  3. pip install fastapi uvicorn pillow numpy

Launch (one worker per GPU, round-robin across workers):
    python launch_sam3_server.py --sam3-root /path/to/sam3 --gpus 0,1,2,3 --port 8787
    python launch_sam3_server.py --sam3-root /path/to/sam3 --num-gpus 4 --port 8787
  --sam3-root defaults to $SAM3_ROOT, else the current directory (run it from the
  sam3 repo root and paths resolve with no flags).

Wire it to the tool (on the machine running the MCP server / agent):
    export SAM3_SERVER_URL=http://<server-host>:8787   # no trailing /segment
    curl http://<server-host>:8787/health              # sanity check

Serves:
    POST /segment        {"image_b64","prompt","score_threshold"?,"return_img"?}
    POST /segment/batch  {"items":[{...}, ...]}   (<= MAX_BATCH_SIZE)
    GET  /health
"""

import os
import io
import base64
import argparse
import logging
import uuid
import asyncio
from typing import Dict, List, Optional

import numpy as np
import torch
import torch.multiprocessing as mp
from PIL import Image, ImageDraw
from fastapi import FastAPI, HTTPException
import uvicorn

COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255),
]

MAX_BATCH_SIZE = 32
MAX_IMAGE_LONG_SIDE = 4096
MAX_CONCURRENT_REQUESTS = 128
REQUEST_TIMEOUT_S = 30
WORKER_RESTART_INTERVAL_S = 5

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger("sam3-multi")

# Resolved in __main__ from CLI/env, then read by workers + the health monitor.
_CHECKPOINT_PATH: Optional[str] = None
_BPE_PATH: Optional[str] = None


def _resolve_paths(sam3_root: str, checkpoint: Optional[str], bpe: Optional[str]) -> tuple[str, str]:
    """Resolve checkpoint + BPE paths from CLI/env, defaulting to the sam3 repo layout."""
    root = os.path.abspath(sam3_root)
    ckpt = checkpoint or os.environ.get("SAM3_CHECKPOINT") or os.path.join(root, "checkpoints", "sam3.pt")
    bpe_path = bpe or os.environ.get("SAM3_BPE_PATH") or os.path.join(root, "sam3", "assets", "bpe_simple_vocab_16e6.txt.gz")
    for label, path in (("checkpoint", ckpt), ("BPE vocab", bpe_path)):
        if not os.path.exists(path):
            raise SystemExit(
                f"SAM3 {label} not found: {path}\n"
                f"Pass --sam3-root / --checkpoint / --bpe (or set SAM3_ROOT / SAM3_CHECKPOINT / SAM3_BPE_PATH)."
            )
    return ckpt, bpe_path


# --------------- GPU Worker Process ---------------

def gpu_worker(gpu_id: int, request_queue: mp.Queue, response_dict, lock, checkpoint_path: str, bpe_path: str):
    """Worker process: loads model on one GPU, processes requests forever."""
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    device = "cuda:0"
    worker_name = f"worker-gpu{gpu_id}"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    wlog = logging.getLogger(worker_name)

    wlog.info(f"Loading SAM3 on physical GPU {gpu_id} (visible as {device})...")
    from sam3.model_builder import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor

    model = build_sam3_image_model(
        bpe_path=bpe_path,
        checkpoint_path=checkpoint_path,
        load_from_HF=False,
        device=device,
    )
    model = model.float().to(device)
    processor = Sam3Processor(model, device=device)
    wlog.info("Model loaded.")

    while True:
        try:
            item = request_queue.get()
            if item is None:
                wlog.info("Shutdown signal received.")
                break

            req_id, image_bytes, prompt, score_threshold, return_img = item

            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
                state = processor.set_image(pil_image)
                output = processor.set_text_prompt(state=state, prompt=prompt)

            masks = output["masks"]
            boxes = output["boxes"]
            scores = output["scores"]

            results = []
            for mask, box, score in zip(masks, boxes, scores):
                if score < score_threshold:
                    continue
                mask_np = mask.cpu().numpy() if isinstance(mask, torch.Tensor) else mask
                if mask_np.ndim == 3:
                    mask_np = mask_np[0]
                mask_img = Image.fromarray((mask_np * 255).astype(np.uint8))
                buf = io.BytesIO()
                mask_img.save(buf, format="PNG")
                results.append({
                    "score": float(score),
                    "box": [float(x) for x in (box.tolist() if hasattr(box, "tolist") else box)],
                    "mask_b64": base64.b64encode(buf.getvalue()).decode(),
                })

            data = {"prompt": prompt, "num_masks": len(results), "results": results}
            if return_img and results:
                data["image_b64"] = _draw_masks(pil_image, results)

            with lock:
                response_dict[req_id] = {"ok": True, "data": data}
        except Exception as e:
            wlog.exception(f"Error processing request {req_id}")
            with lock:
                response_dict[req_id] = {"ok": False, "error": str(e)}


def _draw_masks(image: Image.Image, results: list, alpha: float = 0.45) -> str:
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    for i, r in enumerate(results):
        color = COLORS[i % len(COLORS)]
        mask_bytes = base64.b64decode(r["mask_b64"])
        mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L")
        mask_np = np.array(mask_img) > 127
        colored = np.array(overlay)
        colored[mask_np] = (
            (1 - alpha) * colored[mask_np] + alpha * np.array(color)
        ).astype(np.uint8)
        overlay = Image.fromarray(colored)
        draw = ImageDraw.Draw(overlay)
        x0, y0, x1, y1 = r["box"]
        draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
        label = f'{r["score"]:.2f}'
        draw.rectangle([x0, y0 - 18, x0 + len(label) * 8 + 4, y0], fill=color)
        draw.text((x0 + 2, y0 - 16), label, fill=(255, 255, 255))
    buf = io.BytesIO()
    overlay.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# --------------- FastAPI Server ---------------

app = FastAPI(title="SAM3 Multi-GPU Server", version="2.0")

workers_ready = False
request_queues: List[mp.Queue] = []
response_dict: Optional[Dict] = None
dict_lock: Optional[mp.Lock] = None
worker_processes: List[mp.Process] = []
gpu_ids_list: List[int] = []
num_workers = 0
_rr_counter = 0
_request_semaphore: Optional[asyncio.Semaphore] = None


def _start_single_worker(idx: int, gpu_id: int):
    q = mp.Queue(maxsize=64)
    if idx < len(request_queues):
        request_queues[idx] = q
    else:
        request_queues.append(q)
    p = mp.Process(
        target=gpu_worker,
        args=(gpu_id, q, response_dict, dict_lock, _CHECKPOINT_PATH, _BPE_PATH),
        daemon=True,
    )
    p.start()
    if idx < len(worker_processes):
        worker_processes[idx] = p
    else:
        worker_processes.append(p)
    logger.info(f"Started worker on GPU {gpu_id} (PID {p.pid})")


def start_workers(gpu_ids: List[int], checkpoint_path: str, bpe_path: str, workers_per_gpu: int = 1):
    global request_queues, response_dict, dict_lock, num_workers, workers_ready, gpu_ids_list
    global _CHECKPOINT_PATH, _BPE_PATH

    _CHECKPOINT_PATH = checkpoint_path
    _BPE_PATH = bpe_path

    manager = mp.Manager()
    response_dict = manager.dict()
    dict_lock = mp.Lock()

    idx = 0
    for gpu_id in gpu_ids:
        for _ in range(workers_per_gpu):
            gpu_ids_list.append(gpu_id)
            _start_single_worker(idx, gpu_id)
            idx += 1

    num_workers = idx
    workers_ready = True
    logger.info(
        f"All {num_workers} workers started "
        f"({len(gpu_ids)} GPUs x {workers_per_gpu} workers/GPU)"
    )


def pick_worker() -> int:
    global _rr_counter
    idx = _rr_counter % num_workers
    _rr_counter += 1
    return idx


def _validate_image(image_bytes: bytes) -> Image.Image:
    """Decode and validate image, return PIL Image or raise HTTPException."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Failed to decode image: {e}")
    w, h = img.size
    if max(w, h) > MAX_IMAGE_LONG_SIDE:
        raise HTTPException(
            400,
            f"Image too large: {w}x{h}, max long side is {MAX_IMAGE_LONG_SIDE}. "
            f"SAM3 internally resizes to 1008x1008, sending larger images wastes bandwidth.",
        )
    return img


async def submit_request(image_bytes: bytes, prompt: str, score_threshold: float, return_img: bool = False) -> dict:
    req_id = str(uuid.uuid4())
    worker_idx = pick_worker()

    async with _request_semaphore:
        request_queues[worker_idx].put((req_id, image_bytes, prompt, score_threshold, return_img))

        elapsed = 0.0
        while elapsed < REQUEST_TIMEOUT_S:
            await asyncio.sleep(0.05)
            elapsed += 0.05
            with dict_lock:
                if req_id in response_dict:
                    result = response_dict.pop(req_id)
                    break
        else:
            raise HTTPException(504, f"Request timed out after {REQUEST_TIMEOUT_S}s")

    if not result["ok"]:
        raise HTTPException(500, result["error"])
    return result["data"]


async def _worker_health_monitor():
    """Background task: restart crashed workers."""
    while True:
        await asyncio.sleep(WORKER_RESTART_INTERVAL_S)
        for idx, p in enumerate(worker_processes):
            if not p.is_alive():
                gpu_id = gpu_ids_list[idx]
                logger.warning(f"Worker GPU {gpu_id} (PID {p.pid}) died, restarting...")
                _start_single_worker(idx, gpu_id)


@app.on_event("startup")
async def _start_health_monitor():
    if workers_ready:
        asyncio.create_task(_worker_health_monitor())


@app.on_event("startup")
async def _init_semaphore():
    global _request_semaphore
    _request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


@app.get("/health")
def health():
    alive = sum(1 for p in worker_processes if p.is_alive())
    return {
        "status": "ok",
        "workers_total": num_workers,
        "workers_alive": alive,
        "limits": {
            "max_batch_size": MAX_BATCH_SIZE,
            "max_image_long_side": MAX_IMAGE_LONG_SIDE,
            "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
            "request_timeout_s": REQUEST_TIMEOUT_S,
        },
    }


@app.post("/segment")
async def segment(request: dict):
    """Body: {"image_b64": "...", "prompt": "...", "score_threshold": 0.0, "return_img": false}"""
    image_b64 = request.get("image_b64")
    prompt = request.get("prompt")
    score_threshold = request.get("score_threshold", 0.0)
    return_img = request.get("return_img", False)
    if not image_b64 or not prompt:
        raise HTTPException(400, "Required: image_b64, prompt")
    raw = base64.b64decode(image_b64)
    _validate_image(raw)
    return await submit_request(raw, prompt, score_threshold, return_img)


@app.post("/segment/batch")
async def segment_batch(request: dict):
    """Body: {"items": [{"image_b64": "...", "prompt": "...", "score_threshold": 0.0, "return_img": false}, ...]}"""
    items = request.get("items", [])
    if not items:
        raise HTTPException(400, "Required: items (list of {image_b64, prompt})")
    if len(items) > MAX_BATCH_SIZE:
        raise HTTPException(
            400,
            f"Batch too large: {len(items)} items, max is {MAX_BATCH_SIZE}",
        )

    tasks = []
    for item in items:
        b64 = item.get("image_b64")
        prompt = item.get("prompt")
        threshold = item.get("score_threshold", 0.0)
        ret_img = item.get("return_img", False)
        if not b64 or not prompt:
            raise HTTPException(400, "Each item needs image_b64 and prompt")
        raw = base64.b64decode(b64)
        _validate_image(raw)
        tasks.append(submit_request(raw, prompt, threshold, ret_img))

    results = await asyncio.gather(*tasks)
    return {"num_items": len(results), "results": results}


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser(description="SAM3 Multi-GPU Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--gpus", type=str, default=None,
                        help="Comma-separated GPU IDs, e.g. 0,1,2,3")
    parser.add_argument("--num-gpus", type=int, default=None,
                        help="Use first N GPUs (alternative to --gpus)")
    parser.add_argument("--workers-per-gpu", type=int, default=1,
                        help="Number of worker processes per GPU (default: 1)")
    parser.add_argument("--sam3-root", default=os.environ.get("SAM3_ROOT", "."),
                        help="SAM3 repo root; checkpoint/BPE default to <root>/checkpoints and <root>/sam3/assets (env: SAM3_ROOT)")
    parser.add_argument("--checkpoint", default=None,
                        help="Path to sam3.pt (default: <sam3-root>/checkpoints/sam3.pt; env: SAM3_CHECKPOINT)")
    parser.add_argument("--bpe", default=None,
                        help="Path to BPE vocab .txt.gz (default: <sam3-root>/sam3/assets/...; env: SAM3_BPE_PATH)")
    args = parser.parse_args()

    checkpoint_path, bpe_path = _resolve_paths(args.sam3_root, args.checkpoint, args.bpe)

    if args.gpus:
        gpu_ids = [int(x) for x in args.gpus.split(",")]
    elif args.num_gpus:
        gpu_ids = list(range(args.num_gpus))
    else:
        gpu_ids = list(range(torch.cuda.device_count()))

    logger.info(f"Starting with GPUs: {gpu_ids}, workers_per_gpu: {args.workers_per_gpu}")
    logger.info(f"checkpoint: {checkpoint_path}")
    logger.info(f"bpe:        {bpe_path}")
    start_workers(gpu_ids, checkpoint_path, bpe_path, workers_per_gpu=args.workers_per_gpu)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
