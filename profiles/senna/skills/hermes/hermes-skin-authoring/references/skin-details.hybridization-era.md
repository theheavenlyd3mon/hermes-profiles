# Skin Hybridization Notes — 2026-05-10

Three skins were examined for a custom build combining elements from each. The result is the **oni** skin at `~/.hermes/skins/oni.yaml`.

## Source Skins

### solo-leveling-boss.yaml (24KB, ~18KB banner_hero)
- **Name:** solo-leveling-boss
- **Description:** Shadow Monarch terminal — ARISE. The system has chosen.
- **Palette:** Purple monarchy (#6B21A8, #A855F7, #9F7AE0) on dark (#06030F) with aquamarine accents (#7FFFD4)
- **Spinner faces:** (☾), (⚔), (▰), (⟨⟩), (◈)
- **Thinking verbs:** entering the gate, raising shadow soldiers, extracting shadow, ARISE language
- **Wings:** ⟪☾/☾⟫, ⟪⚔/⚔⟫, ⟨▰/▰⟩
- **Branding:** agent_name "Shadow Monarch", welcome "ARISE. The system has chosen." (purple→cyan gradient), response_label " ☾ MONARCH ", prompt_symbol "☾ "
- **Tool emojis:** terminal ☾, web_search ⫷, read_file 巻, write_file ⚔, search_files ⌖, execute_code ⚡, memory 心, todo_write ▰, task ⟨⟩
- **Banner_logo:** ASCII "SHADOW" wordmark + "SYSTEM ARISE ALONE LEVEL UP" gradient
- **Banner_hero:** Large pixel-art shadow figure (18KB of Braille/block art) — purple/blue/cyan ANSI gradients

### kensei.yaml (18KB, ~12KB banner_hero)
- **Name:** kensei
- **Description:** KENSEI — sword saint. Deep ink, blood lacquer, and drawn steel.
- **Palette:** Blood reds (#8B0000, #E34234, #C0392B) + gold (#D4A017) + parchment (#E8DCC6, #F5F0E8) on deep ink (#0A0A0A)
- **Custom colors:** blade_glow (#EF0131), blade_edge (#F70240) — used in banner art only
- **Spinner faces:** (⚔), (◉), (⌁), (▲)
- **Thinking verbs:** drawing steel, reading the wind, finding stillness, cutting noise, tempering the edge, holding breath
- **Wings:** ⟪⚔/⚔⟫
- **Branding:** agent_name "KENSEI", welcome "Steel drawn. State your objective." (gold→blood gradient), goodbye "Committing seppuku", response_label " ⚔ KENSEI ", prompt_symbol "⚔ "
- **Tool emojis:** terminal ⚔, web_search ◉, read_file 巻
- **Banner_logo:** Block-letter "KENSEI" + "剣 - Blade Mastery - Death before dishonour - 剣" + "━━━━不名誉より死━━━━"
- **Banner_hero:** Large Braille-art katana/samurai figure + decorative border frame with Japanese text: 勇気なき男は、刃なき小刀のごとし (A man without courage is like a knife without a blade)

### netrunner.yaml (7KB, minimal banner_hero)
- **Name:** netrunner
- **Description:** Cyberpunk netrunner — neural interface hacker aesthetic
- **Palette:** Teal/cyan (#00E5FF, #00BCD4) on dark (#05292D) with dark teal (#004D40)
- **Spinner faces:** (◎), (◈), (⬡), (⊕), (⊗)
- **Thinking verbs:** breaching ICE, decrypting subnet, jacking into the NET, spoofing credentials, escalating access
- **Wings:** ⟨◎/◎⟩, ⟨◈/◈⟩, ⟨⬡/⬡⟩, ⟨⌁/⌁⟩
- **Branding:** agent_name "Netrunner Agent", welcome "Connection established. Neural link active. Type your command or /help for protocols." (teal→white gradient), goodbye "Disconnecting neural link.", response_label " ◎ Netrunner ", prompt_symbol "◎ ❯ "
- **Tool emojis:** 14 entries — terminal ◎, web_search ⬡, read_file ◇, write_file ◆, search_files ◈, execute_code ⌁, browser_navigate ⊕, delegate_task ▣, mixture_of_agents ⚗, memory ◐, cronjob ↻, process ⚙, todo ☐
- **Banner_logo:** "NET RUNNER" + "JINTEKI SYSTEMS AGENT" with gradient
- **Banner_hero:** Small Braille skull art with neural cables (1.5KB)

## Resolved Design: ONI Skin

The user wanted a **cyberpunk netrunner who uses a samurai alias** — a digital ghost with a blade.

### Design Decisions

| Element | Decision | Rationale |
|---------|----------|-----------|
| Colors | Full Kensei palette (blood reds + gold) | User explicitly chose this |
| Agent name | "ONI" | Japanese demon mask -- fits both netrunner alias and visual theme |
| Welcome | Hybrid of all 3, leaning netrunner | "Connection established. Neural link active. Blade drawn. State your objective -- or /help for protocols." |
| Welcome gradient | Gold (#D4A017) to blood red (#8B0000) | Kensei colors across the full 86-char message |
| Goodbye | Netrunner-style fade to black | "Connection severed. Neural link terminated. The blade returns to shadow." -- red to black gradient |
| Prompt symbol | (netrunner) | Primary interaction symbol |
| Symbols in tools | (prompt), (terminal), (write_file) | All three visible in tool_emojis and banner |
| Verbs | 14 items mixed from all 3 sources | "breaching the gate", "drawing steel", "jacking into the NET", "raising shadow soldiers" |
| Banner_logo | "ONI" in Doom figlet font | Pulled from asciified API |
| Banner_hero | Oni mask ASCII art (46 lines) | Converted from openclipart PNG via jp2a |

### Tools Used
- `asciified.thelicato.io` API for figlet banner
- `openclipart.org` for oni mask source image (ID 171060 -- "oni mask no color")
- `jp2a` (installed via `brew install jp2a`) with `--width=68 --invert` for image to ASCII
- Python heredoc for gradient color tag generation

### Key Lessons
1. YAML requires `clarify: "?"` (quoted) -- bare `?` is a mapping key trigger
2. jp2a works with PNG despite some docs saying "JPEG only" -- it handles PNG via libpng
3. Openclipart's 800px version gives good ASCII results with `--width=68`
4. `--invert` is essential for white-on-transparent images (common on Openclipart)
5. Em dashes from Python need verification -- `\u2014` in Python output might stay as literal `\u2014` text rather than becoming `-` in the YAML file
6. Gradient welcome text at 86 characters produces a YAML line too long for comfortable editing -- but it works
