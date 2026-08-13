# K12 Visual Asset Catalog

Pre-built HTML/CSS components for K12 math/physics/chemistry tutorial videos. Each component delivers candle-level visual quality: multi-layer gradients, inset shadows, ground reflections, glow halos, and JS-driven animation hooks.

**Usage:** Before writing custom HTML for any visual object, check this catalog. If a matching component exists, copy its CSS + HTML verbatim into your composition. Never reinvent a car, candle, battery, or lens from scratch.

---

## Component Index

### Motion (运动体) — 13 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `car` | 小汽车 | [motion/car.html](components/motion/car.html) | `--paint-a/b`, `--wheel-spin` | `.car-a/b/c` |
| `train` | 火车 | [motion/train.html](components/motion/train.html) | `--paint-a/b`, `--wheel-spin` | — |
| `ball` | 小球 | [motion/ball.html](components/motion/ball.html) | `--ball-color-a/b`, `--spin` | `.ball-blue/red/metal` |
| `boat` | 小船 | [motion/boat.html](components/motion/boat.html) | `--paint-a/b`, `--bob` | `.boat-a/b/c` |
| `bicycle` | 自行车 | [motion/bicycle.html](components/motion/bicycle.html) | `--wheel-spin`, `--paint-a/b` | `.bike-a/b/c` |
| `person` | 人物 | [motion/person.html](components/motion/person.html) | `--skin`, `--shirt`, `--pants` | `.person-a/b/c` |
| `rocket` | 火箭 | [motion/rocket.html](components/motion/rocket.html) | `--thrust`, `--paint-a/b` | `.rocket-a/b` |
| `airplane` | 飞机 | [motion/airplane.html](components/motion/airplane.html) | `--paint-a/b` | `.airplane-a/b` |
| `elevator` | 电梯 | [motion/elevator.html](components/motion/elevator.html) | `--door-open`, `--position-y` | — |
| `conveyor` | 传送带 | [motion/conveyor.html](components/motion/conveyor.html) | `--belt-offset`, `--speed` | — |
| `fan` | 风扇 | [motion/fan.html](components/motion/fan.html) | `--spin`, `--blade-color` | — |
| `gear` | 齿轮 | [motion/gear.html](components/motion/gear.html) | `--spin` | — |
| `helicopter` | 直升机 | [motion/helicopter.html](components/motion/helicopter.html) | `--rotor-spin`, `--paint-a/b` | `.heli-a/b` |

### Optics (光学) — 7 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `candle` | 蜡烛 | [optics/candle.html](components/optics/candle.html) | — | `.candle-inverted` |
| `alcohol-lamp` | 酒精灯 | [optics/alcohol-lamp.html](components/optics/alcohol-lamp.html) | `--flame-on` | `.lamp-off` |
| `lens` | 透镜 | [optics/lens.html](components/optics/lens.html) | `--focal-glow` | `.lens-concave` |
| `light-ray` | 光线 | [optics/light-ray.html](components/optics/light-ray.html) | `--ray-length`, `--ray-color`, `--ray-opacity` | `.ray-incident/refracted/reflected` |
| `prism` | 三棱镜 | [optics/prism.html](components/optics/prism.html) | `--refraction-glow` | — |
| `mirror` | 镜面 | [optics/mirror.html](components/optics/mirror.html) | `--reflection-glow` | `.mirror-concave/convex` |
| `screen` | 光屏 | [optics/screen.html](components/optics/screen.html) | `--image-brightness` | — |

### Circuit (电路) — 21 components

#### Realistic Components (实物图组件) — CSS/HTML

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `bulb` | 灯泡 | [circuit/bulb.html](components/circuit/bulb.html) | `--brightness` | `.bulb-off/dim/on` |
| `battery` | 电池 | [circuit/battery.html](components/circuit/battery.html) | `--voltage-glow` | `.battery-v` |
| `meter` | 电表 | [circuit/meter.html](components/circuit/meter.html) | `--needle-angle` | `.meter-a/v` |
| `switch` | 开关 | [circuit/switch.html](components/circuit/switch.html) | `--switch-angle` | — |
| `rheostat` | 变阻器 | [circuit/rheostat.html](components/circuit/rheostat.html) | `--slider-pos` | — |
| `wire` | 导线 | [circuit/wire.html](components/circuit/wire.html) | `--wire-length`, `--current-glow` | — |
| `resistor` | 电阻 | [circuit/resistor.html](components/circuit/resistor.html) | `--temperature` | — |
| `generator` | 发电机 | [circuit/generator.html](components/circuit/generator.html) | `--shaft-spin`, `--output-glow` | — |
| `motor` | 电动机 | [circuit/motor.html](components/circuit/motor.html) | `--shaft-spin`, `--power-on` | — |
| `transformer` | 变压器 | [circuit/transformer.html](components/circuit/transformer.html) | `--primary-glow`, `--secondary-glow` | — |
| `electromagnet` | 电磁铁 | [circuit/electromagnet.html](components/circuit/electromagnet.html) | `--power`, `--polarity` | — |
| `solenoid` | 螺线管 | [circuit/solenoid.html](components/circuit/solenoid.html) | `--current-flow`, `--field-glow` | — |
| `capacitor` | 电容器 | [circuit/capacitor.html](components/circuit/capacitor.html) | `--charge` | — |
| `led` | LED | [circuit/led.html](components/circuit/led.html) | `--brightness`, `--led-color` | — |
| `fuse` | 保险丝 | [circuit/fuse.html](components/circuit/fuse.html) | `--blown` | — |

#### Schematic Symbols (原理图符号) — SVG snippets

Use these for **circuit schematic diagrams** (电路图). Paste the `<g>` element into your SVG. Read [circuit-schematic-guide.md](../references/circuit-schematic-guide.md) for physics rules (battery polarity, current direction, ammeter/voltmeter wiring).

| ID | Name | File | Notes | Variants |
|----|------|------|-------|----------|
| `sch-battery` | 电池符号 | [circuit/sch-battery.html](components/circuit/sch-battery.html) | **长线=正极(+), 短线=负极(-)** | single cell, two cells |
| `sch-ammeter` | 电流表符号 | [circuit/sch-ammeter.html](components/circuit/sch-ammeter.html) | red circle, must be in SERIES | — |
| `sch-voltmeter` | 电压表符号 | [circuit/sch-voltmeter.html](components/circuit/sch-voltmeter.html) | blue circle, must be in PARALLEL, dashed wires | vertical, horizontal |
| `sch-switch` | 开关符号 | [circuit/sch-switch.html](components/circuit/sch-switch.html) | pivot dot + blade | open, closed |
| `sch-bulb` | 灯泡符号 | [circuit/sch-bulb.html](components/circuit/sch-bulb.html) | circle with X cross | — |
| `sch-resistor` | 电阻符号 | [circuit/sch-resistor.html](components/circuit/sch-resistor.html) | rectangle box | — |

### Mechanics (力学) — 12 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `pulley` | 滑轮 | [mechanics/pulley.html](components/mechanics/pulley.html) | `--spin` | `.pulley-fixed/movable` |
| `spring-meter` | 弹簧测力计 | [mechanics/spring-meter.html](components/mechanics/spring-meter.html) | `--stretch` | — |
| `pendulum` | 摆锤 | [mechanics/pendulum.html](components/mechanics/pendulum.html) | `--angle` | — |
| `balance` | 天平 | [mechanics/balance.html](components/mechanics/balance.html) | `--tilt` | — |
| `weight` | 砝码 | [mechanics/weight.html](components/mechanics/weight.html) | — | `.weight-hook` |
| `weight-set` | 砝码组 | [mechanics/weight-set.html](components/mechanics/weight-set.html) | — | — |
| `wooden-block` | 木块 | [mechanics/wooden-block.html](components/mechanics/wooden-block.html) | `--paint-a/b` | `.wood-a/b/c` |
| `lever` | 杠杆 | [mechanics/lever.html](components/mechanics/lever.html) | `--tilt`, `--fulcrum-pos` | — |
| `force-arrow` | 力箭头 | [mechanics/force-arrow.html](components/mechanics/force-arrow.html) | `--arrow-length`, `--arrow-color` | `.force-gravity/normal/friction` |
| `rope` | 绳子 | [mechanics/rope.html](components/mechanics/rope.html) | `--rope-length`, `--tension` | — |
| `inclined-plane` | 斜面 | [mechanics/inclined-plane.html](components/mechanics/inclined-plane.html) | `--angle` | — |
| `seesaw` | 跷跷板 | [mechanics/seesaw.html](components/mechanics/seesaw.html) | `--tilt` | — |

### Fluid & Thermal (流体热学) — 6 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `thermometer` | 温度计 | [fluid/thermometer.html](components/fluid/thermometer.html) | `--level` | — |
| `beaker` | 烧杯 | [fluid/beaker.html](components/fluid/beaker.html) | `--fill`, `--liquid-color`, `--wave-offset` | — |
| `water-container` | 水槽 | [fluid/water-container.html](components/fluid/water-container.html) | `--level`, `--liquid-color` | — |
| `bubbles` | 气泡 | [fluid/bubbles.html](components/fluid/bubbles.html) | `--bubble-progress` | — |
| `float-block` | 浮沉物块 | [fluid/float-block.html](components/fluid/float-block.html) | `--submersion`, `--bob-offset` | `.fblk-metal` |
| `water-tap` | 水龙头 | [fluid/water-tap.html](components/fluid/water-tap.html) | `--flow` | — |

### Chemistry (化学) — 7 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `flask` | 锥形瓶 | [chemistry/flask.html](components/chemistry/flask.html) | `--fill`, `--liquid-color`, `--bubble-phase` | — |
| `test-tube` | 试管 | [chemistry/test-tube.html](components/chemistry/test-tube.html) | `--fill`, `--liquid-color`, `--tilt` | `.tube-clamped` |
| `graduated-cylinder` | 量筒 | [chemistry/graduated-cylinder.html](components/chemistry/graduated-cylinder.html) | `--level`, `--liquid-color` | — |
| `gas-bottle` | 集气瓶 | [chemistry/gas-bottle.html](components/chemistry/gas-bottle.html) | `--fill`, `--gas-color` | — |
| `funnel` | 漏斗 | [chemistry/funnel.html](components/chemistry/funnel.html) | `--fill`, `--liquid-color`, `--drip-progress` | — |
| `evap-dish` | 蒸发皿 | [chemistry/evap-dish.html](components/chemistry/evap-dish.html) | `--fill`, `--liquid-color`, `--steam-opacity` | — |
| `flame` | 焰色火焰 | [chemistry/flame.html](components/chemistry/flame.html) | `--flame-core/mid/outer/edge/glow-a/glow-b` | `.flame-na/k/cu/ca/sr/ba` |

### Wave (波动) — 4 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `wave-tank` | 水波槽 | [wave/wave-tank.html](components/wave/wave-tank.html) | `--wave-phase`, `--amplitude`, `--wavelength` | — |
| `water-wave` | 水波纹 | [wave/water-wave.html](components/wave/water-wave.html) | `--wave-count`, `--wave-phase`, `--wave-color` | — |
| `sound-wave` | 声波 | [wave/sound-wave.html](components/wave/sound-wave.html) | `--phase`, `--amplitude`, `--frequency` | — |
| `spring-wave` | 弹簧波 | [wave/spring-wave.html](components/wave/spring-wave.html) | `--wave-phase`, `--compression` | — |

### Indicators (指示器) — 8 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `compass` | 指南针 | [indicators/compass.html](components/indicators/compass.html) | `--needle-angle` | — |
| `magnet` | 磁铁 | [indicators/magnet.html](components/indicators/magnet.html) | `--field-glow` | `.magnet-bar/horseshoe` |
| `speaker` | 扬声器 | [indicators/speaker.html](components/indicators/speaker.html) | `--vibration`, `--sound-waves` | — |
| `clock` | 钟表 | [indicators/clock.html](components/indicators/clock.html) | `--hour-angle`, `--minute-angle`, `--second-angle` | — |
| `hourglass` | 沙漏 | [indicators/hourglass.html](components/indicators/hourglass.html) | `--progress`, `--sand-stream` | — |
| `stopwatch` | 秒表 | [indicators/stopwatch.html](components/indicators/stopwatch.html) | `--second-angle`, `--running` | — |
| `ruler` | 直尺 | [indicators/ruler.html](components/indicators/ruler.html) | — | — |
| `protractor` | 量角器 | [indicators/protractor.html](components/indicators/protractor.html) | — | — |

### Math (数学) — 5 components

| ID | Name | File | CSS Vars | Variants |
|----|------|------|----------|----------|
| `graph-axes` | 坐标轴 | [math/graph-axes.html](components/math/graph-axes.html) | `--grid-opacity`, `--axis-color` | — |
| `number-line` | 数轴 | [math/number-line.html](components/math/number-line.html) | `--highlight-pos` | — |
| `dice` | 骰子 | [math/dice.html](components/math/dice.html) | `--face`, `--roll-angle` | — |
| `coin` | 硬币 | [math/coin.html](components/math/coin.html) | `--flip-progress` | — |
| `probability-bag` | 概率袋 | [math/probability-bag.html](components/math/probability-bag.html) | `--open` | — |

### Backgrounds (背景图)

The Aurora Scholar theme uses a **textured aurora mesh** background: the wave texture image provides an organic base layer, and 3 CSS aurora gradient orbs (`filter: blur(80px)`) float on top. See design-system.md "Background Treatment" for the full layer stack and per-scene aurora palette guide.

| ID | Name | File | Tone | Status |
|----|------|------|------|--------|
| `bg-wave` | 蓝色波浪丝带 | [backgrounds/bg-texture.jpg](backgrounds/bg-texture.jpg) | Light blue, flowing 3D ribbons | **Active** |

**Usage:**
1. During Step 5 scaffolding, copy the texture into the project: `cp assets/backgrounds/bg-texture.jpg dist/bg-texture.jpg`
2. Compositions reference it as `../bg-texture.jpg` (relative to `dist/compositions/`)
3. Each scene layers 3 aurora orbs on top of the texture, using a different color palette for visual variety
4. See design-system.md "Background Treatment" for the `.bg-texture` CSS and aurora orb HTML template

---

## Total: 83 components + 1 active background texture across 10 categories

---

## Quality Specification

Every component has:

1. **Multi-layer gradients (>=3 layers)** — radial-gradient spots for highlights + linear-gradient for base color + top highlight wash
2. **Inset shadow** — top edge highlight + bottom darkening for 3D volume
3. **Ground shadow** — `::after` pseudo-element with radial-gradient ellipse
4. **Glow halo** — `filter: drop-shadow()` on root container (essential on light backgrounds for depth)
5. **No CSS @keyframes** — all animation via JS `Math.sin(time * freq)` in renderAt()
6. **Minimum 30px** in smallest dimension at 1920x1080

## How to Use

1. Find matching component in the index above
2. Read the component `.html` file
3. Copy the `<style>` block into your composition's `<style>`
4. Copy the HTML block into your scene container
5. Copy the JS HOOKS into your `renderAt()` function
6. Set CSS vars and position via `style` attribute on the root element
7. Use variant classes for alternate appearances (e.g. `.car-b`, `.meter-v`)

## When No Catalog Match Exists — Quality Fallback Template

If the problem requires a visual object not in this catalog, you MUST create it at candle-level quality using this template. Do NOT use flat single-gradient shapes or CSS @keyframes.

### Required CSS Structure (copy and adapt)

```css
.my-object {
  position: absolute;
  width: 120px;   /* 100-180px for primary objects */
  height: 80px;
  margin-left: -60px;  /* center horizontally */
  transform-origin: 50% 100%;
  z-index: 12;
  /* Glow halo — REQUIRED for depth on light backgrounds */
  filter: drop-shadow(0 14px 22px rgba(0,0,0,0.35));
}

/* Ground shadow — REQUIRED, must stay WITHIN container bounds */
.my-object::after {
  content: "";
  position: absolute;
  left: 6px; right: 6px; bottom: 0;
  height: 10px;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(0,0,0,0.38), transparent 70%);
  z-index: -1;
}

/* Main body — MINIMUM 3 gradient layers */
.my-object-body {
  position: absolute;
  left: 3px; right: 3px; bottom: 8px;
  height: 56px;
  border-radius: 8px;
  background:
    /* Layer 1: highlight spots (radial) */
    radial-gradient(ellipse at 70% 18%, rgba(255,255,255,0.18), transparent 28px),
    /* Layer 2: top highlight wash (linear) */
    linear-gradient(180deg, rgba(255,255,255,0.38), transparent 22%),
    /* Layer 3: bottom darkening (linear) */
    linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.14) 100%),
    /* Layer 4: base color (linear or radial) */
    linear-gradient(135deg, var(--paint-a, #60a5fa), var(--paint-b, #1e3a8a) 70%);
  border: 1px solid rgba(255,255,255,0.2);
  /* Inset shadow — REQUIRED for 3D volume */
  box-shadow:
    inset 0 2px 0 rgba(255,255,255,0.3),    /* top edge highlight */
    inset 0 -14px 20px rgba(2,6,23,0.28),    /* bottom darkening */
    0 8px 18px rgba(30,64,175,0.24);          /* external projection */
}

/* Chrome/highlight strip — adds surface detail */
.my-object-body::after {
  content: "";
  position: absolute;
  left: 10%; right: 10%; top: 30%;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4) 30%, rgba(255,255,255,0.4) 70%, transparent);
}
```

### Required Quality Checklist for New Objects

Before considering a custom object done, verify ALL of these:

- [ ] **≥3 gradient layers** on the main body (not counting pseudo-elements)
- [ ] **Inset shadow** with both top highlight (`inset 0 2px ...`) and bottom darkening (`inset 0 -Npx ...`)
- [ ] **Ground shadow** via `::after` pseudo-element with `radial-gradient(ellipse, ...)`
- [ ] **Glow halo** via `filter: drop-shadow()` on the root container
- [ ] **Border** with subtle white alpha: `border: 1px solid rgba(255,255,255,0.2)`
- [ ] **No CSS @keyframes or transition** — all animation via JS in `renderAt()`
- [ ] **Minimum 30px** in smallest dimension
- [ ] **100-180px tall** for primary objects (15-25% of 780px world panel)
- [ ] **In split/apparatus layouts**, primary apparatus (alcohol lamp, flask, burner) must fill **30-45% of the panel height** — scale with `transform: scale()` if the default size is too small for the container
- [ ] All text/labels use dark colors (`#0f172a` or darker)

### Reference Component for Quality Comparison

If unsure about quality level, read [optics/candle.html](components/optics/candle.html) — it is the gold standard. Compare your custom object's gradient complexity, shadow depth, and surface detail against the candle before finalizing.
