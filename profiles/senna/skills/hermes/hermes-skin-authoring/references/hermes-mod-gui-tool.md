# hermes-mod — Community GUI Skin Editor

**Repo:** https://github.com/cocktailpeanut/hermes-mod
**Author:** cocktailpeanut (Pinokio creator)
**Status:** Early stage (7 commits, 2 months, 133 stars, 8 forks, 2 open issues)
**Launch:** `npx -y hermes-mod`

## What It Is

Web-based visual skin editor. Express server on localhost:3210 that reads/writes `~/.hermes/skins/` YAML files through a browser GUI.

## Tech Stack

- express, figlet (ASCII logos), jimp (image processing), js-yaml
- Optional: ffmpeg (WEBP→PNG), zenity/osascript (file pickers)

## Features

- Visual editing of all skin fields (colors, spinner, branding, tool_emojis)
- Built-in image-to-ASCII/braille hero conversion (4 styles: braille, ascii, blocks, dots)
- Figlet logo generator with 8 font presets (minimal, slant, small, heavy, block, shadow, wide, compact)
- Live YAML preview
- Direct save to `~/.hermes/skins/`
- One-click activate (writes to config.yaml)
- Respects HERMES_HOME env var
- Pinokio integration (install.js, start.js, pinokio.js)

## Limitations vs Our Skill

- No per-character gradient color tags (our block-grouped technique prevents vertical text wrapping)
- No per-profile skin support (`~/.hermes/profiles/<name>/skins/` not mentioned)
- Windows-centric defaults in server.js (HERMES_PYTHON defaults to `env/Scripts/python.exe`)
- No tests, no CI
- Uses Jimp 0.22 (older) — custom JS braille pipeline, less battle-tested than jp2a
- No CLI flags, no help text, no error handling in bin entry

## When to Recommend

- User wants quick skin scaffolding without touching YAML
- User prefers GUI over terminal editing
- User wants to experiment with image-to-banner conversion
- NOT a replacement for our skill for: gradient banners, multi-profile support, surgical edits, deployment lifecycle

## Complementary Workflow

1. Start with hermes-mod to scaffold a skin visually
2. Drop into hermes-skin-authoring skill for advanced gradient work, recoloring, deployment