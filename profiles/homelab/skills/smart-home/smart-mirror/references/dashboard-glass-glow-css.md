# Hermes Dashboard — Liquid Glass CSS (Interim)

> **Status**: Interim implementation. A research task (`t_71c773f5`) has been dispatched to the `researcher` kanban profile to investigate Apple's official Liquid Glass design language (iOS 26 / macOS Tahoe 26) and recommend a more faithful CSS approach. Once findings land, update this reference and the dashboard CSS accordingly.

The user's chosen visual style for the hermes-dashboard module — iOS 26.5 inspired liquid glass. **Clear frosted glass, no color tint.**

## Card Container

```css
.hermes-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 18px;
  border-radius: 14px;
  position: relative;
  overflow: hidden;

  /* Clear frosted glass — no color tint */
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);

  /* Subtle border + inner highlight */
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);

  transition: all 0.3s ease;
}

/* Diagonal shine overlay */
.hermes-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.03) 0%,
    transparent 50%
  );
  pointer-events: none;
  border-radius: 14px;
}
```

## Card Header (title + icon)

```css
.hermes-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.hermes-card-title {
  font-size: 15px;
  font-weight: 400;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  opacity: 0.9;
}

.hermes-card-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 1px;
  opacity: 0.65;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.08));
}
```

## Status Left Border (subtle white variations)

```css
.hermes-card-ready   { border-left: 3px solid rgba(255, 255, 255, 0.15); }
.hermes-card-running { border-left: 3px solid rgba(255, 255, 255, 0.25); }
.hermes-card-done    { border-left: 3px solid rgba(255, 255, 255, 0.15); }
.hermes-card-blocked {
  border-left: 3px solid rgba(255, 107, 107, 0.5);
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 0 24px rgba(255, 107, 107, 0.08);
}
```

## Priority Dot with Glow

```css
.hermes-card-priority-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.hermes-card-priority-high   { background: #ff6b6b; box-shadow: 0 0 8px rgba(255, 107, 107, 0.5); }
.hermes-card-priority-medium { background: #ffd93d; box-shadow: 0 0 6px rgba(255, 217, 61, 0.4); }
.hermes-card-priority-low    { background: #6bcb77; box-shadow: 0 0 4px rgba(107, 203, 119, 0.3); }
```

## Empty State (frosted glass widget)

```css
.hermes-dashboard-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 28px 20px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.hermes-dashboard-empty-icon { font-size: 32px; opacity: 0.6; margin-bottom: 2px; }
.hermes-dashboard-empty-text { font-size: 15px; font-weight: 400; letter-spacing: 0.5px; opacity: 0.7; }
.hermes-dashboard-empty-sub  { font-size: 11px; opacity: 0.4; font-weight: 300; letter-spacing: 0.3px; }
```

## Status Emoji Icons

| Status   | Emoji | CSS class suffix |
|----------|-------|------------------|
| blocked  | 🚫    | `-blocked`       |
| running  | 🔄    | `-running`       |
| ready    | ⚡    | `-ready`         |
| done     | ✅    | `-done`          |

## Meta Row

```css
.hermes-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  font-weight: 300;
  margin-top: 3px;
  position: relative;
  z-index: 1;
}

.hermes-card-assignee {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  opacity: 0.5;
}

.hermes-card-meta-status {
  opacity: 0.35;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}
```

## Offline Indicator

```css
.hermes-dashboard-offline {
  font-size: 13px;
  color: #ff6b6b;
  opacity: 0.8;
  margin-bottom: 4px;
  text-shadow: 0 0 12px rgba(255, 107, 107, 0.3);
  letter-spacing: 0.3px;
}
```
