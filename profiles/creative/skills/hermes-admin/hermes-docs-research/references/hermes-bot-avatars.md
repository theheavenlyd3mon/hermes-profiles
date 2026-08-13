# Hermes bot avatars & desktop-app appearance

Verified against hermes-agent.nousresearch.com docs, 2026-08.

## Core fact

Hermes has NO built-in avatar setting. In bot/messaging mode the avatar is
whatever the platform's bot account carries — set it once in each platform's
admin surface and Hermes' messages appear under it automatically. There is no
`hermes` command or config key for it.

## Per-platform avatar locations

| Platform | Where | Details |
|---|---|---|
| Telegram | Message @BotFather → `/setuserpic` | Companions: `/setdescription`, `/setabouttext`, `/setcommands`. Renaming the bot's @username is picked up by Hermes automatically; the picture is purely BotFather-side. |
| Discord | Developer Portal → app → **Bot** page | Custom avatar + banner upload; that's what users see in servers. |
| WhatsApp (Cloud API) | business.facebook.com/wa/manage/phone-numbers → your number | Profile picture: square, ≥640×640px recommended, updates immediately. Display name goes through Meta's 24–48h name review. CANNOT be set via API — Business Manager only. |
| Google Chat | Google Cloud Console → Chat API → Configuration | **Avatar URL**: any public PNG. |
| Slack | Slack app's Basic Information page | Standard app-icon upload. |

## Recommended avatar sizes (design brief)

Telegram 512×512; Discord displays at 256×256 (upload up to 1024); WhatsApp
≥640×640 square. One master square asset cropped per platform works.

## Desktop app

No avatar/profile-picture setting exists. Assistant identity is the fixed
built-in Hermes branding. Visual customization that DOES exist:
- Themes: Settings → Appearance, incl. live VS Code Marketplace theme importer.
- CLI/TUI skins: `/skin`, `display.skin`, banner palette, prompt glyph/color.
- SOUL.md / `/personality` shape how Hermes SPEAKS — explicitly separate from
  appearance ("SOUL.md and /personality affect how Hermes speaks; display.skin
  and /skin affect how Hermes looks").
