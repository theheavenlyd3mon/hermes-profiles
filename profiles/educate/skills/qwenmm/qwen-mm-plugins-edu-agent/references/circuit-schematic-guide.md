# Circuit Schematic Diagram Guide (电路原理图绘制规范)

Rules for drawing standard K12 physics circuit schematic diagrams (电路图) in SVG. These rules are **mandatory** when a scene requires a circuit schematic — violating them produces physically incorrect diagrams.

## When to Use This Guide

Use this guide (and the `sch-*` SVG templates) when drawing **circuit schematics** (原理图/电路图) — the abstract symbol-based diagrams used in physics textbooks.

Use the existing CSS components (`battery.html`, `meter.html`, `bulb.html`, etc.) when drawing **physical wiring diagrams** (实物连接图) — realistic depictions of actual components and wires.

A single tutorial video often needs BOTH: a schematic in the analysis scene and a realistic wiring diagram in the connection scene.

---

## 1. Battery Symbol (电池符号) — MOST COMMON ERROR SOURCE

```
  -         +          -    +    -    +
  ┃│       ┃│         ┃│  ┃│  ┃│  ┃│
──┃│──     ──┃│──     ──┃│──┃│──┃│──┃│──
  ┃│       ┃│         ┃│  ┃│  ┃│  ┃│
 短粗线   长细线      两节干电池串联
 (neg)    (pos)
```

### Rule: 长线 = 正极(+)，短线 = 负极(-)

| Feature | Positive terminal (+) | Negative terminal (-) |
|---------|----------------------|----------------------|
| Line length | **LONG** (~40px) | **SHORT** (~24px) |
| Line thickness | Thinner (stroke-width: 2.5) | Thicker (stroke-width: 4) |
| Position (default) | RIGHT side | LEFT side |

### Two-cell battery (两节干电池)

Draw two cells in series: `短-长--短-长`. The leftmost short line is the overall negative terminal; the rightmost long line is the overall positive terminal.

### Verification checklist

Before finalizing a battery symbol, verify:
- [ ] The **longer** line has the `+` label next to it
- [ ] The **shorter** line has the `-` label next to it
- [ ] The `+` and `-` labels are on the correct side of the battery (not swapped)
- [ ] If the battery orientation is flipped (e.g., + on left), the wire connections and current arrows are updated accordingly

### SVG template reference

Use `sch-battery.html` from `assets/components/circuit/`. Terminal endpoints:
- Single cell: left `(-24, 0)` = negative, right `(24, 0)` = positive
- Two cells: left `(-40, 0)` = negative, right `(40, 0)` = positive

---

## 2. Current Direction (电流方向)

### Rule: conventional current flows from + to - through the external circuit

```
        ← ← ← ← ← (inside battery: - to +)
       -│          │+
        │  BATTERY │
       -│          │+
        → → → → → → (external circuit: + to -)
            ↓
        Ammeter → Switch → L1 → L2
            ↓
        → → → → → → (back to battery -)
```

**Direction:** Current exits the battery's **positive terminal (+)**, flows through the external circuit (ammeter, switch, bulbs, etc.), and returns to the battery's **negative terminal (-)**.

### Current direction arrows (电流方向箭头)

Current direction arrows must form a **consistent closed loop**. All arrows in the circuit must agree on the same direction of flow.

SVG arrow template (pointing RIGHT):
```xml
<!-- Arrow pointing right: flat base on left, tip on right -->
<polygon points="X-8,Y-6  X-8,Y+6  X+8,Y" fill="#06b6d4"/>
```

To change direction, rotate the triangle:
- **Right:** `points="X-8,Y-6  X-8,Y+6  X+8,Y"` (tip at larger X)
- **Left:** `points="X+8,Y-6  X+8,Y+6  X-8,Y"` (tip at smaller X)
- **Down:** `points="X-6,Y-8  X+6,Y-8  X,Y+8"` (tip at larger Y)
- **Up:** `points="X-6,Y+8  X+6,Y+8  X,Y-8"` (tip at smaller Y)

> ⚠️ The templates above are **standalone `<polygon>` heads** — you rotate the triangle geometry itself, so they always point the way you draw them (safe). If instead you attach the head to a line via a **`<marker orient="auto">`**, the rules are different: `orient="auto"` rotates the marker so its local **`+x` axis follows the line**, so the marker's triangle **must be drawn pointing RIGHT (`+x`)** and let `orient` rotate it. Drawing that marker triangle pointing down/up (`±y`) makes it come out **sideways** on vertical wires. See the arrow rules in `step-5-build-components.md`; the gate `scripts/check_svg_arrow.py` enforces this.

### Verification checklist

After placing all current arrows:
- [ ] Trace the entire loop starting from battery `+` terminal
- [ ] Every arrow points in the direction current flows **away from +** and **toward -**
- [ ] No arrow points backward against the flow
- [ ] Arrows on vertical segments: **down** on the side leaving `+`, **up** on the side returning to `-`(or vice versa depending on layout)
- [ ] Arrows on horizontal segments: consistent with the loop direction

---

## 3. Ammeter (电流表 A)

### Rules
1. **Series only (必须串联)** — the ammeter is part of the main loop, never on a parallel branch
2. **Current enters + terminal (电流从+接线柱流入)** — the `+` terminal faces the battery `+` side
3. **Current exits - terminal (从-接线柱流出)** — the `-` terminal faces away from battery `+`

### SVG template: `sch-ammeter.html`
- Red circle with "A" label
- Default: `+` on left, `-` on right
- Terminal endpoints: `(-50, 0)` and `(50, 0)`

---

## 4. Voltmeter (电压表 V)

### Rules
1. **Parallel only (必须并联)** — the voltmeter connects across the component being measured
2. **+ terminal toward battery + (正接线柱靠近电源正极)** — connect to the higher-potential side
3. **- terminal toward battery - (负接线柱靠近电源负极)** — connect to the lower-potential side
4. **Dashed branch wires (并联支路用虚线)** — use `stroke-dasharray="8,4"` for the wires connecting the voltmeter to the main circuit
5. **Connection wires drawn externally (连接导线由电路布局绘制)** — the voltmeter template has NO built-in wire stubs; all dashed connection wires must be drawn as separate `<line>` or `<path>` elements from the main circuit T-junction point to the voltmeter circle edge. This prevents wires from protruding past the junction.

### SVG template: `sch-voltmeter.html`
- Blue circle with "V" label, **no built-in wire stubs**
- Vertical variant (default for parallel branches) and horizontal variant available
- Terminal endpoints at the **circle edge**: `(0, -30)` and `(0, 30)` for vertical; `(-30, 0)` and `(30, 0)` for horizontal

### Correct vs Wrong voltmeter wiring (电压表接线正确 vs 错误)

The voltmeter has no built-in wire stubs. Draw all dashed connection wires externally, ending exactly at the circle edge. Wires must NOT extend past the T-junction on the main circuit wire.

```xml
<!-- ✅ CORRECT: dashed wires from junction to circle edge, no protrusion -->
<!-- Voltmeter centered at (450, 350), main circuit vertical wires at x=370 and x=530 -->
<g class="sch-voltmeter-h" transform="translate(450, 350)">
  <circle cx="0" cy="0" r="30" fill="rgba(37,99,235,0.06)" stroke="#2563eb" stroke-width="3"/>
  <text x="0" y="9" text-anchor="middle" font-size="32" font-weight="700" fill="#2563eb">V</text>
</g>
<!-- Left dashed wire: from junction (370, 350) to circle edge (420, 350) -->
<line x1="370" y1="350" x2="420" y2="350"
      stroke="#1a1f36" stroke-width="3" stroke-dasharray="8,4"/>
<!-- Right dashed wire: from circle edge (480, 350) to junction (530, 350) -->
<line x1="480" y1="350" x2="530" y2="350"
      stroke="#1a1f36" stroke-width="3" stroke-dasharray="8,4"/>

<!-- ❌ WRONG: wire stubs built into the component extend past the junction -->
<!-- If terminal endpoints were at ±50 and main wire is at x=400,
     the left stub extends to x=400 (450-50), overlapping/protruding past the junction -->
```

### Voltmeter positioning rule (电压表定位规则)

When placing a voltmeter on a parallel branch:
1. Determine the two T-junction points on the main circuit wire (where the branch diverges)
2. Position the voltmeter **centered between** the two junctions, and **align its terminals horizontally or vertically** with the junction points — this allows straight dashed lines and avoids L-shaped routing
3. Draw dashed `<line>` elements from each junction point to the nearest circle edge (center ± 30)
4. The dashed wires must **start at the junction** and **end at the circle edge** — never extend beyond either point
5. **Draw a filled junction dot** (`<circle r="4" fill="#0f172a"/>`) at each T-junction point on the main wire — this visually confirms the parallel branch is connected to the main circuit
6. **If L-shaped routing is unavoidable**, use a single `<path d="M ... L ... L ...">` with `stroke-dasharray` and `stroke-linejoin="round"` — never two separate `<line>` elements (they create gaps/protrusions at corners)

---

## 5. Switch (开关 S)

### Rules

1. **Switch must break the circuit path (开关必须断开导线).** The incoming wire ends at the switch **pivot** terminal; the outgoing wire starts at the **contact** terminal. Never draw a continuous wire from one side of the switch straight through to the other — that makes the switch decorative and the circuit permanently closed.
2. **No zero-length wire segments.** Every `<line>` must have distinct start and end coordinates. A line like `x1="750" y1="180" x2="750" y2="180"` draws nothing and is a bug.
3. **Switch orientation must match the wire direction (开关方向与导线方向一致).** If the switch is on a horizontal wire, the blade opens upward/downward from horizontal. If the switch is on a **vertical** wire, rotate the switch 90° so the blade opens sideways from vertical. Never draw a horizontal switch on a vertical wire.
4. **Open terminal is part of the circuit path.** When the switch closes, the blade connects the pivot to the contact terminal. The outgoing wire must start from the **contact** terminal, not from the pivot.

### SVG template: `sch-switch.html`
- Open: blade angled up, contact point is hollow circle
- Closed: blade horizontal, contact point is solid circle
- Terminal endpoints: `(-40, 0)` and `(40, 0)`

### Correct vs Wrong switch wiring

```xml
<!-- ✅ CORRECT: wire stops at pivot, resumes at contact terminal -->
<line x1="100" y1="200" x2="100" y2="280"/>  <!-- incoming wire to pivot -->
<circle cx="100" cy="280" r="5" fill="#0f172a"/>  <!-- pivot -->
<line x1="100" y1="280" x2="140" y2="250" stroke-width="3"/>  <!-- blade (open) -->
<circle cx="140" cy="280" r="5" fill="none" stroke="#0f172a"/>  <!-- contact -->
<line x1="140" y1="280" x2="140" y2="360"/>  <!-- outgoing wire from contact -->

<!-- ❌ WRONG: continuous wire goes straight through, switch is decoration -->
<line x1="100" y1="200" x2="100" y2="360"/>  <!-- wire passes through switch -->
<circle cx="100" cy="280" r="5"/>  <!-- pivot sits ON the wire -->
<line x1="100" y1="280" x2="140" y2="250"/>  <!-- blade -->
<circle cx="140" cy="280" r="5"/>  <!-- contact not on circuit path -->
```

---

## 6. Bulb (灯泡 L)

### SVG template: `sch-bulb.html`
- Circle with X cross inside
- Label below (L1, L2, etc.)
- Terminal endpoints: `(-48, 0)` and `(48, 0)`

---

## 7. Resistor (电阻 R)

### SVG template: `sch-resistor.html`
- Rectangle box
- Label below (R, R1, R2, etc.)
- Terminal endpoints: `(-44, 0)` and `(44, 0)`

---

## 7b. Rheostat / Slider Rheostat (滑动变阻器 / 变阻器)

Extremely common in K12 电学实验 (伏安法测电阻, 探究电流与电压/电阻关系). There is a
realistic component (`assets/components/circuit/rheostat.html`) but **no `sch-` symbol** —
draw the schematic symbol inline.

### Schematic symbol
- A resistor **rectangle box** with a **slider arrow on top**: an arrow (`marker-end`) that
  points DOWN onto the middle of the box top edge — this arrow is what distinguishes a
  rheostat from a plain resistor. Label **R'** or **滑动变阻器** below.
- Terminal endpoints: same as resistor `(-44, 0)` / `(44, 0)` for the two lower posts used.

### Rules — MOST COMMON ERROR: duplication
1. **Exactly ONE rheostat per circuit (整个电路只有一个滑动变阻器)** — a standard experiment
   uses a single 滑动变阻器 in series. **Never draw two 变阻器 boxes** (e.g. one on the bottom
   edge and one on the left edge of the loop). This is the #1 rheostat error and is gated by
   `check_circuit_inventory.py`.
2. **In series (串联接入干路)** — insert it into ONE wire segment of the main loop, like the
   ammeter. It replaces a section of wire, it is not appended outside the loop.
3. **Do not confuse with the measured resistor R** — the rheostat (控制电流的 R') and the
   measured/fixed resistor (待测/定值 R) are TWO DIFFERENT components with different roles;
   label them distinctly (R' / 变阻器 vs R), and each appears once.
4. **Never add a second rheostat to fill an empty side of the rectangular loop** — an empty
   side is just a wire (导线).

---

## 8. Wire Layout Rules (导线布局)

1. **Right angles only (导线只走横平竖直)** — no diagonal wires in schematic diagrams
2. **Rectangular loop (矩形回路)** — the main circuit forms a rectangle
3. **No crossing wires (导线不交叉)** — rearrange component placement to avoid crossings
4. **Junction dots (交叉连接点用实心圆点)** — where wires actually connect, draw a filled circle (r=4)
5. **Wire path as SVG `<path>`** — use `M`, `L` commands with rounded joins: `stroke-linejoin="round"`
6. **Distribute components around all sides (元件均匀分布在矩形各边)** — do NOT stack all series components on one side of the rectangle. Distribute them across the top, right, bottom, and left edges. A standard textbook layout for 4+ components uses 2-3 sides. **But never invent/duplicate a component to fill a side — an empty side is just a wire (空边只走导线，不得为凑版面加元件).**
7. **No duplicate/overlapping wire segments (禁止重复绘制导线)** — each wire segment between two component terminals must be drawn exactly once. Never draw a full-side wire AND per-component wire segments that cover the same path.

### Standard Textbook Layout Patterns (标准教科书布局)

#### Pattern A: Series circuit (串联电路) — battery on top

```
      (-)  Battery  (+)
    ┌──┤├──┤├──┤├──┬─── Switch S ──┐
    │                                │
    │                               L₁
    │                                │
  Ammeter A                         L₂
    │                                │
    └────────────────────────────────┘
```

Components distributed across **3 sides**: battery+switch on top, L₁+L₂ on right, ammeter on left. Current flows: `+ → right → S → down → L₁ → L₂ → bottom left → up through A → back to -`.

#### Pattern B: Series circuit — linear top (top-heavy layout)

```
    (-)  Battery  (+) ── S ── L₁ ── L₂
     │                                │
     │                                │
     └──────────── A ─────────────────┘
```

All series components on the **top wire**, ammeter on the **bottom return wire**. Clean and simple for circuits with many series components.

#### Pattern C: With voltmeter parallel branch (带电压表)

```
      (-)  Battery  (+) ── S ──┐
       │                        │
       │                       L₁
       │                        │
       │                 ┌── V ──┤  (dashed wires)
       │                 │       │
       │                 └──────L₂
       │                        │
       └──────── A ─────────────┘
```

Voltmeter V is on a **dashed-line branch** parallel to L₂, clearly separated from the main circuit path. The dashed branch must be visually distinct — never squeeze the voltmeter inline between components.

### Layout anti-pattern: all components on one side (反例)

```
    ┌── Battery ──┐
    │              │
    │              S    ← All 4 components
    │              │      stacked on the
    │             L₁      right side!
    │              │
    │             L₂
    │              │
    └──── A ──────┘

    ❌ WRONG: S, L₁, L₂ all on right side.
              Hard to read, non-standard.
```

---

## 9. Wire-Component Segmentation (导线-元件分段规则) — MOST CRITICAL RULE

### The #1 cause of incorrect circuit diagrams

**Wires must STOP at component terminals.** Each component (battery, switch, bulb, ammeter, etc.) has two terminal endpoints. The wire segment arriving at the component must end at terminal A; the wire segment leaving the component must start at terminal B. The component symbol itself visually connects A to B.

**Never draw a continuous wire that passes through a component.** If a single `<path>` or `<line>` spans the full length of one side of the rectangle, it will visually draw a wire straight through every component on that side — making the components look like stickers pasted on top of a wire, not properly wired into the circuit.

### Rule: one wire segment per gap between components

For a side of the rectangle with N components, you need **N+1** wire segments:

```
terminal → wire₁ → [Component₁] → wire₂ → [Component₂] → wire₃ → terminal
```

Example: right side has Switch S and Bulb L₁

```xml
<!-- ✅ CORRECT: 3 separate wire segments, stopping at each component -->
<line x1="700" y1="90"  x2="700" y2="160"/>  <!-- corner to switch pivot -->
<!-- switch symbol at y=160~200 -->
<line x1="700" y1="200" x2="700" y2="280"/>  <!-- switch contact to L₁ top terminal -->
<!-- L₁ symbol at y=280~320 -->
<line x1="700" y1="320" x2="700" y2="470"/>  <!-- L₁ bottom terminal to bottom corner -->

<!-- ❌ WRONG: one continuous line through everything -->
<path d="M 700 90 L 700 470"/>  <!-- passes through switch AND L₁ -->
<!-- switch and L₁ drawn on top — decorative only, not wired in -->
```

### SVG implementation pattern

```xml
<!-- PATTERN: Segmented wiring for a series circuit -->
<!-- Each wire segment is a separate <line> or <path> between two terminal endpoints -->

<!-- Segment: top-right corner to switch pivot -->
<line x1="700" y1="90" x2="700" y2="SWITCH_TERMINAL_A" stroke="#0f172a" stroke-width="3.5"/>

<!-- Switch symbol (connects SWITCH_TERMINAL_A to SWITCH_TERMINAL_B internally) -->
<!-- ... switch SVG ... -->

<!-- Segment: switch contact terminal to L₁ terminal A -->
<line x1="700" y1="SWITCH_TERMINAL_B" x2="700" y2="L1_TERMINAL_A" stroke="#0f172a" stroke-width="3.5"/>

<!-- L₁ symbol (connects L1_TERMINAL_A to L1_TERMINAL_B internally) -->
<!-- ... bulb SVG ... -->

<!-- Segment: L₁ terminal B to next component or corner -->
<line x1="700" y1="L1_TERMINAL_B" x2="700" y2="NEXT_POINT" stroke="#0f172a" stroke-width="3.5"/>
```

### Wire-drawing animation (stroke-dashoffset via `attr:{}`)

When using `stroke-dashoffset` animation to progressively reveal wires, each animated path must also follow the segmentation rule. Do NOT create a single full-side path for animation — animate each segment separately, staggered in time. **Always use `attr:{"stroke-dashoffset": ...}` — never the raw camelCase `strokeDashoffset` property**, because GSAP may fail to animate the SVG attribute when it is passed as a CSS property:

```javascript
// ✅ CORRECT: animate each segment with attr:{} wrapper
tl.to("#wire-corner-to-switch", { attr: {"stroke-dashoffset": 0}, duration: 0.8 }, 2.0);
tl.to("#wire-switch-to-l1",    { attr: {"stroke-dashoffset": 0}, duration: 0.8 }, 2.8);
tl.to("#wire-l1-to-corner",    { attr: {"stroke-dashoffset": 0}, duration: 0.8 }, 3.6);

// ❌ WRONG: one path covering the entire side
tl.to("#wire-right-side", { attr: {"stroke-dashoffset": 0}, duration: 2.0 }, 2.0);

// ❌ WRONG: raw camelCase property (will NOT render in HyperFrames)
tl.to("#wire-corner-to-switch", { strokeDashoffset: 0, duration: 0.8 }, 2.0);
```

---

## 10. Common Series Circuit Example (串联电路完整示例)

Problem: L1 and L2 in series, ammeter measures total current, voltmeter measures L1 voltage.

```xml
<svg viewBox="0 0 700 540" xmlns="http://www.w3.org/2000/svg" fill="none">
  <!-- Main rectangular wire loop -->
  <path d="M 440 70 L 580 70 L 580 470 L 120 470 L 120 70 L 260 70"
        stroke="#0f172a" stroke-width="3.5" fill="none"
        stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Battery at top center: - on left (x=260), + on right (x=440) -->
  <!-- Cell 1: long line at x=260 (POSITIVE side of cell 1) -->
  <line x1="260" y1="46" x2="260" y2="94" stroke="#0f172a" stroke-width="2.5"/>
  <!-- Cell 1: short line at x=280 (NEGATIVE side of cell 1) -->
  <line x1="280" y1="56" x2="280" y2="84" stroke="#0f172a" stroke-width="4"/>
  <!-- Internal connection -->
  <line x1="280" y1="70" x2="300" y2="70" stroke="#0f172a" stroke-width="3.5"/>
  <!-- Cell 2: long line at x=300 -->
  <line x1="300" y1="46" x2="300" y2="94" stroke="#0f172a" stroke-width="2.5"/>
  <!-- Cell 2: short line at x=320 -->
  <line x1="320" y1="56" x2="320" y2="84" stroke="#0f172a" stroke-width="4"/>
  <!-- Wire from cell 2 short line to right -->
  <line x1="320" y1="70" x2="440" y2="70" stroke="#0f172a" stroke-width="3.5"/>
  <!--
    ⚠️  Overall polarity:
    LEFT end (x=260) has the long line of cell 1 → but this is actually
    the INTERNAL positive plate of cell 1. In a two-cell series:
      leftmost long line = overall POSITIVE terminal
      rightmost short line = overall NEGATIVE terminal

    WAIT — this depends on how the cells are oriented!
    Standard series connection: cell1(+) connects to cell2(-) internally.

    Correct labeling for this layout:
      x=260 (leftmost line, LONG) → overall + terminal
      x=320 (rightmost line, SHORT, connects to x=440) → overall - terminal

    But the wire runs RIGHT from x=320/440 and loops down — so current
    flows FROM the + terminal at x=260, LEFT to x=120, DOWN, across BOTTOM,
    UP the right side through ammeter/switch, back to - terminal at x=440.

    OR: flip the battery so + is on the right for conventional "current
    flows right-then-down" layout.
  -->

  <!-- RECOMMENDED: Use sch-battery-2 template positioned with
       translate(350, 70) so + is on the right side at x=440 -->

  <!-- ... remaining components use sch-* templates ... -->
</svg>
```

**Simplified approach:** Position the battery with `+` on the RIGHT side of the top wire. Then current naturally flows: right → down → left → up → back to battery `-` on the left. This is the most intuitive rectangular layout for Chinese textbook circuit diagrams.

---

## 11. Pre-Flight Checklist (电路原理图完成前检查)

Run this checklist before considering any circuit schematic scene complete:

### Physics correctness
- [ ] Battery: long line has `+` label, short line has `-` label
- [ ] Battery: `+` and `-` text positions match the physical symbol (not swapped)
- [ ] Current arrows: ALL form a consistent closed loop from `+` to `-` through external circuit
- [ ] Current arrows: no arrow points against the flow direction
- [ ] Ammeter: wired in SERIES (part of the main loop, not on a branch)
- [ ] Ammeter: `+` terminal faces the battery `+` side (current enters `+`)
- [ ] Voltmeter: wired in PARALLEL (on a branch across the measured component)
- [ ] Voltmeter: `+` terminal on the higher-potential side (closer to battery `+`)
- [ ] Voltmeter: branch wires use dashed lines (`stroke-dasharray`)
- [ ] Voltmeter: **no built-in wire stubs** — dashed connection wires are drawn externally from junction to circle edge (±30), never protruding past the T-junction on the main wire

### Visual quality
- [ ] All wire segments are horizontal or vertical (no diagonals)
- [ ] Wire stroke-width >= 3px
- [ ] Component labels (L1, L2, S, etc.) are clearly visible (font-size >= 22px)
- [ ] Terminal `+`/`-` labels use contrasting colors (red for `+`, blue for `-`)
- [ ] SVG elements sized for 1080p video (min 30px in any dimension)

### Wire segmentation (导线分段) — CRITICAL
- [ ] **No continuous wire passes through any component** — each wire segment ends at a component terminal
- [ ] **Switch properly interrupts the wire** — incoming wire ends at pivot, outgoing wire starts at contact terminal, no wire bridges the gap
- [ ] **No zero-length line segments** — every `<line>` has distinct start and end coordinates
- [ ] **Switch orientation matches wire direction** — horizontal switch on horizontal wire, vertical switch on vertical wire
- [ ] **No duplicate/overlapping wires** — each gap between components is drawn exactly once
- [ ] **Components distributed across multiple sides** — series components are NOT all stacked on one side of the rectangle
- [ ] **Voltmeter on a visually separate branch** — dashed wires clearly diverge from main path, voltmeter is not squeezed inline between components

---

## 12. Physical Wiring Diagram Rules (实物连接图规则)

Sections 1–11 cover **circuit schematics** (原理图/电路图) — abstract symbol-based diagrams. This section covers **physical wiring diagrams** (实物连接图) — realistic depictions of actual components connected by wires, commonly used in "连接电表" and "连接主回路" operation scenes.

### When to use physical wiring diagrams

- **"Connect the circuit" operation scenes (连接主回路/连接电表)** → physical wiring diagram
- **"Analyze the circuit" principle scenes (电路分析)** → circuit schematic (sections 1–11)
- A tutorial video often needs BOTH: schematic in the analysis scene, physical diagram in the operation scene

### Pre-built components (MUST USE)

Use the realistic CSS components from [assets/ASSET_CATALOG.md](../assets/ASSET_CATALOG.md):

| Component | Asset ID | Variant | Notes |
|-----------|----------|---------|-------|
| Battery | `battery` | `.battery-v` | Metallic cylinder, `--voltage-glow` |
| Ammeter | `meter` | `.meter-a` | Red bezel, `--needle-angle` 0–90 |
| Voltmeter | `meter` | `.meter-v` | Blue bezel, `--needle-angle` 0–90 |
| Switch | `switch` | — | `--switch-angle` 0=open, 45=closed |
| Bulb | `bulb` | `.bulb-off/dim/on` | `--brightness` 0–1 |
| Wire | `wire` | `.wire-v` | `--current-glow` |

If using simplified SVG representations instead of the full CSS components, the **layout rules below still apply**.

### 12.1 Rectangular Loop Layout (矩形回路布局) — SAME PRINCIPLE AS SCHEMATICS

Physical wiring diagrams MUST use a rectangular loop, just like schematics. The realistic components sit on the edges of the rectangle. **Never lay all components in a single horizontal line.**

```
    ┌── [Battery] ── [Switch S] ──┐
    │                              │
    │                             [L₁]
    │                              │
    │                             [L₂]
    │                              │
    └──────── [Ammeter A] ────────┘
```

Components are distributed across **at least 2–3 sides** of the rectangle. The ammeter is on the return wire (bottom or left side), NOT floating outside the loop.

### 12.2 Ammeter Placement (电流表位置) — MUST BE IN THE LOOP

The ammeter must be **ON the main circuit loop wire**, typically on the bottom return wire between the last component and the battery's negative terminal. It is part of the series circuit.

```
    ❌ WRONG: ammeter floating outside the loop

    [Battery]──[S]──[L₁]──[L₂]        [A] ← floating
         │                   │           │
         └───────────────────┘──────────┘
                                 ↑ wire extends far beyond components

    ✅ CORRECT: ammeter ON the return wire

    [Battery]──[S]──┐
         │           │
         │          [L₁]
         │           │
         │          [L₂]
         │           │
         └──[A]─────┘
              ↑ ammeter is part of the loop
```

**Rules:**
1. Ammeter is inserted INTO a wire segment of the main loop — it replaces a section of wire, not appended outside
2. The loop bounding box should tightly enclose all components — no wire routing that extends 300+ pixels beyond the rightmost/bottommost component
3. Current enters the ammeter's `+` terminal (from the battery `+` side)

### 12.3 Voltmeter Placement (电压表位置) — SEPARATE PARALLEL BRANCH

The voltmeter connects in parallel across the measured component. Its branch wires must be **visually distinct** from the main loop.

```
    ✅ CORRECT: voltmeter below on clear parallel branch

    ──[L₁]──┬──[L₂]──┬──
             │         │
             │   [V]   │    ← dashed wires, clearly separate
             │         │
             └─────────┘

    ❌ WRONG: voltmeter squeezed inline

    ──[L₁]──[V]──[L₂]──    ← looks like V is in series
```

**Rules:**
1. Voltmeter is placed OUTSIDE the main loop, on a branch that runs parallel to the measured component
2. Branch wires use dashed lines (`stroke-dasharray="8,4"`) or a different color to distinguish from main circuit wires
3. The branch should be at least 80px away from the main wire to avoid visual confusion
4. `+` terminal toward higher potential (battery `+` side)
5. **T-junction dots are mandatory (T型分支点必须有实心圆点)** — where each dashed branch wire meets the main circuit wire, draw a filled circle (`r="5"`, same color as the wire) centered exactly ON the main circuit wire coordinates. Without junction dots, the parallel branch looks disconnected/floating.
6. **Dashed wires must terminate exactly ON the main circuit wire (虚线必须终止于主回路导线坐标)** — the endpoint coordinates of each dashed wire must lie on the main circuit wire's path. If the main vertical wire is at `x=580`, the dashed wire's endpoint x-coordinate must be exactly `580`, not `575` or `585`. Any offset makes the junction look disconnected.
7. **L-shaped routing uses single `<path>` (L型转角用单条path)** — when a dashed wire needs a right-angle turn (because the voltmeter terminal doesn't align horizontally/vertically with the junction), use a single `<path>` element with `stroke-dasharray` rather than two separate `<line>` elements. Two separate lines create visible gaps or overlaps at the corner.
8. **Prefer straight-line connections (优先直线连接)** — position the voltmeter so that its terminals align horizontally or vertically with the T-junction points, allowing simple straight dashed lines. Only use L-shaped routing when alignment is impossible.

### Correct vs Wrong voltmeter branch wiring (电压表并联支路接线示例)

```xml
<!-- ✅ CORRECT: straight dashed wires + junction dots on main wire -->
<!-- Main vertical wire at x=580, voltmeter centered at (450, 350) -->
<!-- T-junction between L₁ and L₂ at (580, 300), below L₂ at (580, 400) -->

<!-- Junction dots ON the main wire -->
<circle cx="580" cy="300" r="5" fill="#06b6d4"/>
<circle cx="580" cy="400" r="5" fill="#06b6d4"/>

<!-- Upper dashed wire: junction (580, 300) → voltmeter top terminal -->
<!-- Voltmeter terminal aligns at y=300, so straight horizontal line -->
<line x1="580" y1="300" x2="480" y2="300"
      stroke="#06b6d4" stroke-width="3" stroke-dasharray="8,4"/>

<!-- Lower dashed wire: junction (580, 400) → voltmeter bottom terminal -->
<line x1="580" y1="400" x2="480" y2="400"
      stroke="#06b6d4" stroke-width="3" stroke-dasharray="8,4"/>

<!-- ❌ WRONG — L-shaped route with two separate lines, no junction dot -->
<!-- Gap/protrusion appears at the corner, junction looks floating -->
<line x1="480" y1="320" x2="580" y2="320"
      stroke="#06b6d4" stroke-width="3" stroke-dasharray="8,4"/>
<line x1="580" y1="320" x2="580" y2="300"
      stroke="#06b6d4" stroke-width="3" stroke-dasharray="8,4"/>
<!-- No junction dot at (580, 300) → branch looks disconnected from main wire -->

<!-- ⚠️ FALLBACK — if L-shaped routing is unavoidable, use single <path> + junction dot -->
<circle cx="580" cy="300" r="5" fill="#06b6d4"/>
<path d="M 480,350 L 580,350 L 580,300"
      stroke="#06b6d4" stroke-width="3" stroke-dasharray="8,4"
      fill="none" stroke-linecap="round" stroke-linejoin="round"/>
```

### 12.4 "Existing Circuit + New Meters" Scene Pattern (已有电路 + 新增电表)

This is the most common meter connection scene: show an existing circuit (dimmed), then animate new meters being inserted.

**Rules for the dimmed existing circuit:**
1. The existing circuit MUST maintain a **rectangular loop shape** — NOT a flat horizontal line
2. Use dimmed/gray styling: `fill="rgba(200,200,200,0.3)"`, `stroke="#94a3b8"`, `stroke-width="2"`
3. Components are distributed around the rectangle (battery on top, bulbs on right/bottom, etc.)

**Rules for new meter insertion:**
1. The ammeter appears at its correct position IN the existing loop (e.g., on the bottom wire)
2. The existing wire at that position "breaks" and the ammeter is inserted between the two ends
3. New connection wires use bright colors (cyan `#06b6d4`) with glow filter
4. Animation sequence: meter fades in with scale → wires draw to connect → needle deflects (elastic easing)

**Layout template for "existing circuit + ammeter + voltmeter":**

```
    ┌──── [Battery](dimmed) ───── [S](dimmed) ────┐
    │                                               │
    │                                              [L₁](dimmed)
    │                                               │
    │                          ┌── [V](bright) ──┐  │    ← dashed branch
    │                          │                  │  │
    │                          └────────────────[L₂](dimmed)
    │                                               │
    └────────────── [A](bright) ───────────────────┘
                       ↑ inserted into bottom return wire
```

### 12.5 Wire Routing Constraints (导线路由约束)

1. **Compact bounding box**: All wires must stay within a bounding box that is at most ~100px larger than the component area on each side. Never route a wire 400+ pixels beyond the outermost component.
2. **No redundant routing**: If the ammeter is at the bottom of the loop, the return wire goes directly from the last component DOWN to the ammeter level and LEFT to the ammeter, then LEFT to the battery. No routing to the far right first.
3. **Wire-component segmentation applies**: All rules from Section 9 (wires stop at terminals) apply equally to physical wiring diagrams.
4. **Consistent wire width**: Main circuit wires use `stroke-width: 4` with glow filter; dimmed existing wires use `stroke-width: 2.5` without glow.

### 12.6 Physical Wiring Diagram Pre-Flight Checklist

Before considering any physical wiring diagram scene complete:

- [ ] **Component inventory matches the problem (元件清单与题目一致)** — list the components the problem's circuit actually has, then confirm the diagram draws exactly that set. **Single-instance instruments (变阻器/滑动变阻器, 电流表 A, 电压表 V, 开关, 电源) each appear EXACTLY ONCE** — drawing two 变阻器 (or two ammeters, two switches…) in one loop is a physics error. Only genuine multiples (两个灯泡 L₁/L₂, 两个电阻 R₁/R₂) may repeat. Gated by `check_circuit_inventory.py`.
- [ ] **Loop is CLOSED — power source both terminals wired (回路闭合 / 电源两端都接线)** — trace the main loop from the 电源 `+` terminal through every component and back to the 电源 `-` terminal; **every gap has a wire**. The power source has TWO terminals — BOTH must connect to a wire (a very common miss is the segment that runs up the left side back to the source). No unwired component terminal. Gated by `check_circuit_closed.py`.
- [ ] **No dangling wire stub (无悬空导线)** — every wire endpoint lands exactly on a component terminal or meets another wire at a corner; never a wire end floating in empty space. When wire coordinates are animated from a JS `wires` array, the *final* coordinates (not the zero-length placeholders) must form the closed loop.
- [ ] **An empty side of the loop is JUST a wire** — do NOT add or duplicate a component to "fill"/"balance" a side of the rectangle. A rectangular loop with components on 2–3 sides and plain wire on the 4th is correct.
- [ ] Circuit forms a **rectangular loop** — NOT a flat horizontal line
- [ ] Ammeter is **ON the main loop wire** (typically bottom return wire), NOT floating outside
- [ ] Voltmeter is on a **separate branch** with dashed wires, NOT inline between components
- [ ] Voltmeter branch wires have **T-junction dots** (filled circle r=5) at every point where dashed wires meet the main circuit wire
- [ ] Voltmeter dashed wire endpoints are **exactly ON the main circuit wire coordinates** — no offset
- [ ] Voltmeter dashed wires use **straight lines** (preferred) or a **single `<path>`** for L-shaped routes — never two separate `<line>` elements meeting at a corner
- [ ] Voltmeter is positioned so its terminals **align** with junction points (minimizing L-shaped routing)
- [ ] Wire routing is **compact** — bounding box tight around components (≤100px margin)
- [ ] Components are **distributed across 2–3 sides** of the rectangle
- [ ] "Existing circuit" (if dimmed) uses **rectangular loop shape**, not a straight line
- [ ] New meters inserted by **breaking existing wire** at the correct position
- [ ] Used **pre-built CSS components** from ASSET_CATALOG (battery, meter, switch, bulb, wire)
- [ ] Ammeter `+` terminal faces battery `+` side (current enters `+`)
- [ ] Voltmeter `+` terminal on higher-potential side
- [ ] Meter needle animated with `elastic.out` easing
- [ ] No wires pass through components — segmentation rules (Section 9) apply
