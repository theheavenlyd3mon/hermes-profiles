# Suno Personas Workflow

**Source:** Suno official docs, Jack Righteous blog (Dec 2025 update)
**Loaded by:** `suno-music-creation` skill

---

## What Personas Are

Personas save the "essence" of a song — especially **vocals and overall style** — for reuse across generations. They are NOT custom voice training on uploaded recordings.

---

## How to Create a Persona

1. Find a source song with **clear, stable vocals** (not buried under heavy effects or stacked harmonies)
2. More Actions (triple-dot menu) → Create → Make Persona
3. **Toggle to Private** — Personas are public by default
4. Name it (e.g., "RIVEN Voice v1", "SOLA Voice)
5. Add avatar + description (optional but helpful)

---

## How to Use Personas Effectively

1. Select the Persona in Custom Mode (above the lyrics field)
2. Suno auto-fills the Style field with the Persona's style details
3. **Edit the Style field intentionally** — don't treat it as final
4. Follow the **2026 Prompt Balance Rule**:

> **Persona = artist identity** — keep it consistent across songs.
> **Style prompt = producer brief** — change per song.
> Don't let them compete.

| Scenario | Style Field Tag Count |
|----------|----------------------|
| With Persona active | 4–7 essential tags |
| Without Persona | 8–15 tags with full description |

---

## Persona + DSL Hybrid Workflow

The Style field combines three layers:

```
[Persona auto-fills vocal/production identity]
$S(x)$ lifecycle dE/dx>0 → b=1 → 0,
[DSL layer lines: L0-L5 with plain English texture],
[4–7 genre/tempo/key tags]
```

---

## Credit-Safe Testing Workflow

Before burning credits on full songs:

1. Run **2–3 short tests** with the Persona
2. Keep Style field minimal — 1–2 genres, 1 mood line, 2–4 instruments
3. Test **one variable at a time**: tempo feel OR drums OR harmony color
4. Save what works → Persona + stable prompt = your default template

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Genre isn't landing | Strip Style field to 4–5 essential tags |
| Vocals are fuzzy | Shorten lyric lines, reduce dense phrasing |
| Songs sound too similar | Change ONE variable per song (tempo, drums, harmony) |
| Style drifts on Extend | Restate genre/mood in the extension's Style field |
| Prompt and Persona fight | Reduce Style field tags — let Persona carry identity |
