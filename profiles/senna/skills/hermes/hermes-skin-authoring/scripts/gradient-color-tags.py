#!/usr/bin/env python3
"""
Generate block-grouped Hermes skin color tags for banners.

Hermes TUI uses inline [#HEX]text[/] tags for gradient coloring. Per-character
tags inflate source line length ~14x, causing TUI banner wrapp to render text
vertically. This script groups characters into blocks for compact source lines.

Usage:
    python3 gradient-color-tags.py "text to color" "#D4A017" "#8B0000" --block-size 4
    python3 gradient-color-tags.py "勇気なき男は" "#D4A017" "#8B0000" --block-size 2
    python3 gradient-color-tags.py --list-lines "line1|line2|line3" "#D4A017" "#8B0000"

Arguments:
    text          Text to apply gradient to
    start_color   Hex start color (e.g., #D4A017)
    end_color     Hex end color (e.g., #8B0000)
    --block-size  Characters per color tag (default: 3; 2 for CJK, 4 for English)
    --list-lines  Pipe-separated lines to process independently
"""

import sys
import argparse


def lerp_color(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colors at ratio t (0.0-1.0)."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def gradient_block(text: str, c1: str, c2: str, block_size: int = 3) -> str:
    """Apply gradient color in blocks of block_size chars instead of per-character.

    Returns a string of Hermes color tags like:
        [#D19916]A ma[/][#CB8D14]n wi[/][#C68112]thou[/]...

    This reduces source line length by ~60% vs per-character tagging while
    preserving the same visual gradient.
    """
    if not text:
        return ""
    result = ""
    n = len(text)
    i = 0
    while i < n:
        chunk = text[i:i + block_size]
        # Use midpoint of chunk for gradient position
        t = (i + len(chunk) / 2) / n
        color = lerp_color(c1, c2, min(t, 1.0))
        result += f"[{color}]{chunk}[/]"
        i += block_size
    return result


def show_length_comparison(text: str, c1: str, c2: str, block_size: int):
    """Show old vs new source length for context."""
    per_char = ""
    n = len(text)
    for i, ch in enumerate(text):
        t = i / (n - 1) if n > 1 else 0
        col = lerp_color(c1, c2, t)
        per_char += f"[{col}]{ch}[/]"

    grouped = gradient_block(text, c1, c2, block_size)

    print(f"  Rendered chars: {n}")
    print(f"  Per-char source:  {len(per_char):>4} bytes  ({len(per_char)//max(n,1):>2}x overhead)")
    print(f"  Block-grouped:    {len(grouped):>4} bytes  ({len(grouped)//max(n,1):>2}x overhead)")
    print(f"  Reduction:         ~{int((1 - len(grouped)/len(per_char))*100)}% shorter")
    print()
    print(f"  Output: {grouped}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate block-grouped gradient color tags for Hermes skin banners.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("text", type=str, help="Text to apply gradient to")
    parser.add_argument("start_color", type=str, help='Start hex color (e.g., #D4A017)')
    parser.add_argument("end_color", type=str, help='End hex color (e.g., #8B0000)')
    parser.add_argument("--block-size", type=int, default=3,
                        help="Characters per color tag (default: 3; 2 for CJK, 4 for English)")
    parser.add_argument("--list-lines", action="store_true",
                        help="Interpret text as pipe-separated lines, process separately")

    args = parser.parse_args()
    c1 = args.start_color
    c2 = args.end_color

    if args.list_lines:
        lines = args.text.split("|")
        for line in lines:
            if line.strip():
                print(f"--- Line: \"{line}\" ({len(line)} chars) ---")
                show_length_comparison(line, c1, c2, args.block_size)
    else:
        print(f"--- Text: \"{args.text}\" ({len(args.text)} chars) ---")
        show_length_comparison(args.text, c1, c2, args.block_size)


if __name__ == "__main__":
    main()
