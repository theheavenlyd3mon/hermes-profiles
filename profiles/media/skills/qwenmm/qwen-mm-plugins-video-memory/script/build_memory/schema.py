"""Data structures for Hierarchical Graph Memory."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MicroEvent:
    event_id: str
    event_type: str
    time_range: list[float]
    subject: str
    object: str
    action: str
    description: str
    macro_id: str = ""


@dataclass
class Entity:
    entity_id: str
    name: str | None
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    visual_grounding: dict[str, Any] = field(default_factory=dict)
    macro_id: str = ""


@dataclass
class Edge:
    source_id: str
    target_id: str
    relation_label: str
    relation_type: str
    description: str = ""


@dataclass
class OnScreenText:
    text_id: str
    text: str
    time_range: list[float] = field(default_factory=list)
    description: str = ""
    macro_id: str = ""


@dataclass
class Subgraph:
    macro_id: str
    micro_events: list[MicroEvent] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    on_screen_texts: list[OnScreenText] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


@dataclass
class MacroEvent:
    macro_id: str
    label: str
    time_range: list[float]
    summary: str = ""
    key_entities: list[dict[str, str]] = field(default_factory=list)
    event_types: list[str] = field(default_factory=list)
    ocr_texts: list[str] = field(default_factory=list)
    dense_description: str = ""
    asr_text: str = ""
    subgraph: Subgraph | None = None
    super_id: str = ""


@dataclass
class SuperEvent:
    super_id: str
    label: str
    description: str = ""
    sub_macro_ids: list[str] = field(default_factory=list)
    time_range: list[float] = field(default_factory=list)
    key_entities: list[dict[str, str]] = field(default_factory=list)


@dataclass
class VideoRoot:
    title: str = ""
    description: str = ""
    themes: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    emotional_tone: str = ""


@dataclass
class MacroRelation:
    source: str
    target: str
    type: str
    reason: str


@dataclass
class SuperRelation:
    source: str
    target: str
    type: str
    reason: str


@dataclass
class HierarchicalGraphMemory:
    video_key: str = ""
    video_path: str = ""
    root: VideoRoot = field(default_factory=VideoRoot)
    super_events: list[SuperEvent] = field(default_factory=list)
    macro_events: list[MacroEvent] = field(default_factory=list)
    macro_relations: list[MacroRelation] = field(default_factory=list)
    super_relations: list[SuperRelation] = field(default_factory=list)

    def save(self, path: str):
        # Atomic write: a reader (query server) sees the file only once complete.
        tmp = f"{path}.tmp"
        with open(tmp, "w") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path: str) -> HierarchicalGraphMemory:
        with open(path) as f:
            data = json.load(f)

        if "root_event" in data:
            return cls._load_hierarchical(data)

        mem = cls()
        mem.video_key = data.get("video_key", "")
        mem.video_path = data.get("video_path", "")

        r = data.get("root", {})
        mem.root = VideoRoot(
            title=r.get("title", ""),
            description=r.get("description", ""),
            themes=r.get("themes", []),
            key_entities=r.get("key_entities", []),
            emotional_tone=r.get("emotional_tone", ""),
        )

        for se in data.get("super_events", []):
            mem.super_events.append(
                SuperEvent(
                    super_id=se["super_id"],
                    label=se["label"],
                    description=se.get("description", ""),
                    sub_macro_ids=se.get("sub_macro_ids", []),
                    time_range=se.get("time_range", []),
                    key_entities=se.get("key_entities", []),
                )
            )

        for me in data.get("macro_events", []):
            sg_data = me.get("subgraph")
            sg = None
            if sg_data:
                on_screen_texts = []
                for t in sg_data.get("on_screen_texts", []):
                    on_screen_texts.append(
                        OnScreenText(
                            text_id=t.get("text_id", ""),
                            text=t.get("text", ""),
                            time_range=t.get("time_range", []),
                            description=t.get("description", ""),
                            macro_id=me["macro_id"],
                        )
                    )
                sg = Subgraph(
                    macro_id=sg_data.get("macro_id", me["macro_id"]),
                    micro_events=[MicroEvent(**e) for e in sg_data.get("micro_events", [])],
                    entities=[Entity(**e) for e in sg_data.get("entities", [])],
                    on_screen_texts=on_screen_texts,
                    edges=[Edge(**e) for e in sg_data.get("edges", [])],
                )
            mem.macro_events.append(
                MacroEvent(
                    macro_id=me["macro_id"],
                    label=me["label"],
                    time_range=me.get("time_range", []),
                    summary=me.get("summary", ""),
                    key_entities=me.get("key_entities", []),
                    event_types=me.get("event_types", []),
                    ocr_texts=me.get("ocr_texts", []),
                    dense_description=me.get("dense_description", ""),
                    asr_text=me.get("asr_text", ""),
                    subgraph=sg,
                    super_id=me.get("super_id", ""),
                )
            )

        for mr in data.get("macro_relations", []):
            mem.macro_relations.append(MacroRelation(**mr))
        for sr in data.get("super_relations", []):
            mem.super_relations.append(SuperRelation(**sr))

        return mem

    @classmethod
    def _load_hierarchical(cls, data: dict) -> HierarchicalGraphMemory:
        """Load from legacy hierarchical_graph_final.json format."""
        mem = cls()
        mem.video_key = data.get("graph_id", "")

        def _wrap_entities(ents: list) -> list[dict]:
            return [e if isinstance(e, dict) else {"name": e} for e in ents]

        r = data.get("root_event", {})
        mem.root = VideoRoot(
            title=r.get("title", ""),
            description=r.get("description", ""),
            themes=r.get("themes", []),
            key_entities=_wrap_entities(r.get("key_entities", [])),
            emotional_tone=r.get("emotional_tone", ""),
        )

        macro_to_super: dict[str, str] = {}
        for se in data.get("super_events", []):
            super_id = se.get("node_id", "")
            for mid in se.get("sub_macro_ids", []):
                macro_to_super[mid] = super_id
            mem.super_events.append(
                SuperEvent(
                    super_id=super_id,
                    label=se.get("label", ""),
                    description=se.get("description", ""),
                    sub_macro_ids=se.get("sub_macro_ids", []),
                    time_range=se.get("time_range", []),
                    key_entities=_wrap_entities(se.get("key_entities", [])),
                )
            )

        for me in data.get("macro_events", []):
            macro_id = me.get("node_id", "")

            # Synthesize subgraph from inline hierarchical data
            micro_events = []
            evt_ids = me.get("subevent_ids", [])
            evt_summaries = me.get("event_summaries", [])
            for j, evt_id in enumerate(evt_ids):
                desc = evt_summaries[j] if j < len(evt_summaries) else ""
                micro_events.append(
                    MicroEvent(
                        event_id=evt_id,
                        event_type="action",
                        time_range=me.get("time_range", []),
                        subject="",
                        object="",
                        action=desc[:80] if desc else evt_id,
                        description=desc,
                        macro_id=macro_id,
                    )
                )

            entities = []
            ent_names = me.get("key_entity_names", [])
            ent_types = me.get("key_entity_types", [])
            if not ent_names:
                ent_names = [e["name"] if isinstance(e, dict) else str(e) for e in me.get("key_entities", [])]
            for j, name in enumerate(ent_names):
                ent_type = ent_types[j] if j < len(ent_types) else "unknown"
                entities.append(
                    Entity(
                        entity_id=f"ent_{j + 1:03d}",
                        name=name,
                        entity_type=ent_type,
                        description=name,
                        macro_id=macro_id,
                    )
                )

            on_screen_texts = []
            for j, txt in enumerate(me.get("ocr_texts", [])):
                on_screen_texts.append(
                    OnScreenText(
                        text_id=f"ocr_{j + 1:03d}",
                        text=txt,
                        time_range=me.get("time_range", []),
                        description=txt,
                        macro_id=macro_id,
                    )
                )

            sg = (
                Subgraph(
                    macro_id=macro_id,
                    micro_events=micro_events,
                    entities=entities,
                    on_screen_texts=on_screen_texts,
                )
                if (micro_events or entities)
                else None
            )

            mem.macro_events.append(
                MacroEvent(
                    macro_id=macro_id,
                    label=me.get("label", ""),
                    time_range=me.get("time_range", []),
                    summary=me.get("summary", ""),
                    key_entities=_wrap_entities(me.get("key_entities", [])),
                    event_types=me.get("event_types", []),
                    ocr_texts=me.get("ocr_texts", []),
                    dense_description=me.get("dense_description", ""),
                    asr_text=me.get("asr_text", ""),
                    subgraph=sg,
                    super_id=macro_to_super.get(macro_id, ""),
                )
            )

        for mr in data.get("macro_relations", []):
            mem.macro_relations.append(
                MacroRelation(
                    source=mr.get("source_id", mr.get("source", "")),
                    target=mr.get("target_id", mr.get("target", "")),
                    type=mr.get("relation_type", mr.get("type", "")),
                    reason=mr.get("reason", ""),
                )
            )
        for sr in data.get("super_relations", []):
            mem.super_relations.append(
                SuperRelation(
                    source=sr.get("source_id", sr.get("source", "")),
                    target=sr.get("target_id", sr.get("target", "")),
                    type=sr.get("relation_type", sr.get("type", "")),
                    reason=sr.get("reason", ""),
                )
            )

        return mem

    def get_all_nodes(self) -> list[dict]:
        """Get all entity, event, OCR, and ASR nodes for embedding."""
        nodes = []
        for me in self.macro_events:
            if not me.subgraph:
                continue
            for ent in me.subgraph.entities:
                nodes.append(
                    {
                        "node_id": ent.entity_id,
                        "node_type": "entity",
                        "text": f"{ent.name or ''}: {ent.description}",
                        "macro_id": me.macro_id,
                    }
                )
            for ev in me.subgraph.micro_events:
                nodes.append(
                    {
                        "node_id": ev.event_id,
                        "node_type": "event",
                        "text": f"{ev.action}: {ev.description}",
                        "macro_id": me.macro_id,
                    }
                )
            for ocr in me.subgraph.on_screen_texts:
                nodes.append(
                    {
                        "node_id": ocr.text_id,
                        "node_type": "on_screen_text",
                        "text": f"{ocr.text}: {ocr.description}",
                        "macro_id": me.macro_id,
                    }
                )
        import re

        for me in self.macro_events:
            if not me.asr_text:
                continue
            text = me.asr_text.strip()
            if len(text) < 3:
                continue
            chunks: list[str] = []
            current = ""
            sentences = re.split(r"(?<=[.!?。！？\n])\s*", text)
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if current and len(current) + len(sent) > 500:
                    chunks.append(current)
                    current = sent
                else:
                    current = (current + " " + sent).strip() if current else sent
            if current:
                chunks.append(current)
            for idx, chunk in enumerate(chunks):
                if len(chunk) < 3:
                    continue
                nodes.append(
                    {
                        "node_id": f"asr_{me.macro_id}_{idx:03d}",
                        "node_type": "asr_text",
                        "text": chunk,
                        "macro_id": me.macro_id,
                    }
                )
        return nodes
