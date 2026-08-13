# Geometry Construction Guide (几何图形构造参考)

Patterns for computing mathematically exact SVG geometry in HyperFrames compositions, extracted from verified Manim examples. Every coordinate MUST be computed — never estimated by eye.

## Three-Phase Construction

Every geometry scene follows three phases:

1. **Compute** — solve the problem's constraints and produce all vertex coordinates
2. **Assert** — verify every constraint (perpendicularity, parallelism, ratios, collinearity)
3. **Render** — write the SVG using only the computed coordinates

This maps to the existing workflow in step-5-build-components.md (Steps 1–4). This guide provides the **computation recipes** that Step 1 needs.

---

## Pattern 1: Triangle with Perpendicular / Angle Bisector

**Problem type:** Triangle ABC, perpendicular from vertex, angle bisector, midpoints.

```javascript
// Example: △ABC, ∠C = 45°, AB perpendicular bisector meets BC at D, AC perpendicular bisector meets AC at G
// Given: B at origin, BC along x-axis, C at (9, 0)

// Step 1: Choose coordinate system — place one side along x-axis
var B = [0, 0];
var C = [9, 0];

// Step 2: Compute remaining vertices from constraints
// ∠C = 45° means CA direction is at 135° from positive x-axis (interior angle)
// If BC = 9 and AC needs to be determined, solve from the problem
var F = [6, 0];           // perpendicular foot on BC
var A = [6, 3];           // from AF ⊥ BC, AF computed from constraints

// Step 3: Derived points
var D = [3.75, 0];        // AB perpendicular bisector ∩ BC
var E = [(A[0]+B[0])/2, (A[1]+B[1])/2];  // midpoint of AB
var G = [(A[0]+C[0])/2, (A[1]+C[1])/2];  // midpoint of AC
```

**SVG coordinate mapping:** Choose viewBox so the figure is centered. Typical: `viewBox="0 0 600 400"`, with a shift to center the figure.

---

## Pattern 2: Quadrilateral / Parallelogram / Rhombus

**Problem type:** Parallelogram ABCD with diagonals, perpendicularity conditions, fold/rotation.

```javascript
// Example: Parallelogram ABCD, AC ⊥ BD, CF = 5, DF = 12 (where F = diag intersection)
// Use the diagonals as the basis vectors

var scale = 0.28;  // adjust to fit viewBox
var cx = 300, cy = 250;  // center of figure

// Diagonal half-lengths from problem: CF = 5, DF = 12
// AC ⊥ BD → diagonals are perpendicular
// Place diagonals along tilted axes for visual appeal

var AC_half = 5 * scale * 40;   // scaled to SVG units
var BD_half = 12 * scale * 40;

// F is the intersection point (center for parallelogram)
var F = [cx, cy];

// For a general tilt, use rotation
var tilt = -Math.PI / 7;  // slight tilt for visual interest
var cos_t = Math.cos(tilt), sin_t = Math.sin(tilt);

// AC direction (tilted)
var A = [cx - AC_half * cos_t, cy - AC_half * sin_t];
var C = [cx + AC_half * cos_t, cy + AC_half * sin_t];

// BD perpendicular to AC (tilted 90°)
var B = [cx - BD_half * (-sin_t), cy - BD_half * cos_t];
var D = [cx + BD_half * (-sin_t), cy + BD_half * cos_t];

// Assert: AC ⊥ BD
var ac = [C[0]-A[0], C[1]-A[1]];
var bd = [D[0]-B[0], D[1]-B[1]];
var dot = ac[0]*bd[0] + ac[1]*bd[1];
// dot should be ≈ 0
```

**Rhombus special case:** All four sides equal. If ∠A = 60°, place via diagonals:
- Short diagonal = side length (for 60° angle)
- Long diagonal = side × √3

```javascript
// Rhombus with ∠A = 60°, side = s
var s = 200;  // SVG units
var d1 = s;           // short diagonal (between 60° vertices)
var d2 = s * Math.sqrt(3);  // long diagonal (between 120° vertices)

var O = [cx, cy];     // diagonals intersect at center
var A = [cx - d2/2, cy];         // left vertex (60°)
var C = [cx + d2/2, cy];         // right vertex (60°)
var B = [cx, cy - d1/2];         // top vertex (120°)
var D = [cx, cy + d1/2];         // bottom vertex (120°)
```

---

## Pattern 3: Circle Geometry (圆的几何)

**Problem type:** Circle with diameter, tangent lines, inscribed angles, chord intersections.

```javascript
// Example: ⊙O with diameter AB = 8, C on circle, AC = 4, tangent at C
var r = 4;  // radius = diameter / 2

// Place O at center
var O = [cx, cy];
var A = [cx - r * svgScale, cy];
var B = [cx + r * svgScale, cy];

// C on circle: compute angle from AC = 4
// AC = 4 = AB/2 = radius → triangle OAC is equilateral
// so ∠AOC = 60° → C at 120° from positive x-axis
var angleC = 120 * Math.PI / 180;
var C = [cx + r * svgScale * Math.cos(angleC),
         cy - r * svgScale * Math.sin(angleC)];  // y-up in math, y-down in SVG

// Tangent at C: perpendicular to OC
var OC = [C[0] - O[0], C[1] - O[1]];
var tangent_dir = [OC[1], -OC[0]];  // rotate 90°
var tangent_unit = normalize(tangent_dir);

// Point D: intersection of BD ⊥ tangent, where BD passes through B
// Parametric: B + t * tangent_perp direction, must lie on tangent line through C
// Solve for intersection
```

**Key formula — tangent perpendicular to radius:**
```
OC_dir = normalize(C - O)
tangent_dir = [-OC_dir[1], OC_dir[0]]  // 90° rotation
```

---

## Pattern 4: Rotation and Transformation (旋转变换)

**Problem type:** Rotate triangle COD about O by angle θ to get C'OD'.

```javascript
// Rotation of point P about center O by angle theta
function rotatePoint(P, O, theta) {
    var dx = P[0] - O[0];
    var dy = P[1] - O[1];
    var cos_t = Math.cos(theta);
    var sin_t = Math.sin(theta);
    return [
        O[0] + dx * cos_t - dy * sin_t,
        O[1] + dx * sin_t + dy * cos_t
    ];
}

// Example: rotate C and D about O by 30° counterclockwise
var theta = 30 * Math.PI / 180;
var C_prime = rotatePoint(C, O, theta);
var D_prime = rotatePoint(D, O, theta);

// Assert: OC = OC' and OD = OD' (distances preserved)
// Assert: angle between OC and OC' = theta
```

---

## Pattern 5: Line Intersection (直线交点)

**Problem type:** Find intersection of two lines defined by endpoints.

```javascript
// Intersection of line P1–P2 and line P3–P4
function lineIntersection(P1, P2, P3, P4) {
    var d1 = [P2[0] - P1[0], P2[1] - P1[1]];
    var d2 = [P4[0] - P3[0], P4[1] - P3[1]];
    var det = d1[0] * d2[1] - d1[1] * d2[0];
    if (Math.abs(det) < 1e-10) return null;  // parallel
    var dx = P3[0] - P1[0];
    var dy = P3[1] - P1[1];
    var t = (dx * d2[1] - dy * d2[0]) / det;
    return [P1[0] + t * d1[0], P1[1] + t * d1[1]];
}

// Example: find F = AE ∩ BD
var F = lineIntersection(A, E, B, D);
```

---

## Pattern 6: Perpendicular Foot (垂足)

**Problem type:** Drop perpendicular from point P to line AB, find foot H.

```javascript
// Perpendicular foot from P onto line AB
function perpendicularFoot(P, A, B) {
    var AB = [B[0] - A[0], B[1] - A[1]];
    var AP = [P[0] - A[0], P[1] - A[1]];
    var t = (AP[0] * AB[0] + AP[1] * AB[1]) / (AB[0] * AB[0] + AB[1] * AB[1]);
    return [A[0] + t * AB[0], A[1] + t * AB[1]];
}

// Example: CD ⊥ AB, D is the foot
var D = perpendicularFoot(C, A, B);
```

---

## Pattern 7: Reflection / Fold (翻折/对称)

**Problem type:** Fold parallelogram along diagonal AC, point B maps to B'.

```javascript
// Reflect point P across line AB
function reflectPoint(P, A, B) {
    var foot = perpendicularFoot(P, A, B);
    return [2 * foot[0] - P[0], 2 * foot[1] - P[1]];
}

// Example: fold along AC, B maps to B'
var B_prime = reflectPoint(B, A, C);

// Find E: intersection of AB' and CD
var E = lineIntersection(A, B_prime, C, D);
```

---

## Pattern 8: Inclined Plane / Wedge (斜面) — draw it RIGHT-SIDE-UP

**Problem type:** a wedge / ramp / "两个斜面对接成三角形", an object resting on or sliding down a slope, incline force diagrams (斜面受力示意图).

> 🧭 **THE #1 incline bug: drawing the wedge upside-down (斜面画反了).** A real incline is a
> **solid wedge sitting on the ground: the horizontal BASE is at the BOTTOM, the peak is at the
> TOP.** Because SVG's y-axis points DOWN, that means the two base corners have the **LARGEST y**
> (they sit low on screen) and the apex/peak has the **SMALLEST y** (high on screen). A very common
> failure is a triangle with its flat edge on top and the point at the bottom
> (e.g. `points="110,140 590,140 350,440"`) — that is a **funnel/valley floating base-up in the
> air**, i.e. the slope is mirrored/inverted. Real bug seen: "两个斜面对接成三角形" rendered as a
> downward-pointing triangle, so the object appeared stuck to the underside and the normal force
> pointed the wrong way.

**Correct orientation — base on the ground, peak at top:**

```html
<!-- viewBox 0 0 700 520.  GROUND is the bottom base y=430; PEAK apex at top (small y). -->
<!-- Single incline (right-angle wedge): right angle at the bottom-right, slope rises to the left. -->
<polygon points="120,430 620,430 620,150" fill="rgba(6,182,212,0.06)"
         stroke="#94a3b8" stroke-width="2" stroke-linejoin="round"/>
<!--   (120,430)=bottom-left toe   (620,430)=bottom-right (right angle)   (620,150)=top peak -->
<line x1="120" y1="430" x2="620" y2="150" stroke="#06b6d4" stroke-width="6"/>  <!-- the slope surface -->

<!-- "两个斜面对接成三角形" = a HILL: flat base on the ground, TWO slopes meeting at a TOP apex. -->
<polygon points="110,430 590,430 350,150" fill="rgba(6,182,212,0.06)"
         stroke="#94a3b8" stroke-width="2"/>
<!--   base (110,430)-(590,430) on the ground;  apex (350,150) at the TOP.
       LEFT slope = (110,430)->(350,150) ;  RIGHT slope = (590,430)->(350,150).
       An object released on the RIGHT slope slides DOWN toward (590,430). -->
```

**Force diagram on a slope (object resting on the upper surface):**

- **Gravity G** — always straight DOWN from the object's centre: `(x,y) → (x, y+len)`.
- **Normal force N** — perpendicular to the slope surface, pointing **UP and AWAY from the surface**
  (out of the wedge, toward the side the object sits on). On any incline the object rests on TOP,
  so **N always has an upward (negative-y in SVG) component — N must never point downward.** For a
  RIGHT slope rising to the left, N points up-**right**; for a LEFT slope rising to the right, N
  points up-**left**. (If you drew N pointing down or into the wedge, your slope is inverted.)
- **Smooth/光滑 incline** → only G and N (no friction f). **Rough incline** → add friction f along the
  surface, opposing motion (up-slope for an object sliding down).

```javascript
// N direction = outward unit normal of the slope surface segment P1->P2,
// chosen to point AWAY from the wedge interior (centroid) and UPWARD.
function outwardNormal(P1, P2, centroid) {
  var dx = P2[0]-P1[0], dy = P2[1]-P1[1], L = Math.hypot(dx,dy);
  var n = [dy/L, -dx/L];                         // one perpendicular
  var mx=(P1[0]+P2[0])/2, my=(P1[1]+P2[1])/2;    // surface midpoint
  // flip so it points from the interior (centroid) OUTWARD (toward the object)
  if ((n[0]*(mx-centroid[0]) + n[1]*(my-centroid[1])) < 0) n = [-n[0], -n[1]];
  return n;   // sanity: n[1] should be < 0 (upward) for an object on top of the slope
}
// <!-- GEOMETRY VERIFICATION -->
// ASSERT base_is_at_bottom: max(y of base verts) > apex.y   (wedge sits on the ground)
// ASSERT N_points_up: N.dy < 0                              (support force has an upward component)
// ASSERT N_perp_surface: dot(N, slopeDir) == 0
```

**Incline self-check (do before rendering):** base edge horizontal and at the BOTTOM (largest y);
apex/peak at the TOP (smallest y); object drawn ON the outer (upper) face of the slope; N points
up-and-out (never down); G straight down; friction only if the surface is rough.

---

## Angle Arc Construction (角度弧线)

### SVG Arc for Non-Right Angles

Use the cross-product method (SKILL.md Rule 22) to determine sweep direction. Here is the complete JavaScript code for use in HyperFrames compositions:

```javascript
// Draw angle arc at vertex V between arms VP1 and VP2
// Returns SVG path d attribute
function angleArc(V, P1, P2, radius) {
    var dx1 = P1[0] - V[0], dy1 = P1[1] - V[1];
    var dx2 = P2[0] - V[0], dy2 = P2[1] - V[1];

    // Cross product determines sweep direction (SVG y-down coordinates)
    var cross = dx1 * dy2 - dy1 * dx2;
    var sweepFlag = cross > 0 ? 1 : 0;

    // Arc endpoints on each arm
    var angle1 = Math.atan2(dy1, dx1);
    var angle2 = Math.atan2(dy2, dx2);
    var sx = V[0] + radius * Math.cos(angle1);
    var sy = V[1] + radius * Math.sin(angle1);
    var ex = V[0] + radius * Math.cos(angle2);
    var ey = V[1] + radius * Math.sin(angle2);

    // large-arc-flag: 0 for angles < 180°, 1 for reflex angles
    var angleDiff = Math.abs(angle2 - angle1);
    if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
    var largeArc = angleDiff > Math.PI ? 1 : 0;

    return 'M ' + sx.toFixed(1) + ',' + sy.toFixed(1) +
           ' A ' + radius + ',' + radius + ' 0 ' + largeArc + ',' + sweepFlag +
           ' ' + ex.toFixed(1) + ',' + ey.toFixed(1);
}
```

### Angle Label Placement

Place the angle value text at the midpoint of the arc, offset outward from the vertex:

```javascript
function angleLabelPosition(V, P1, P2, offset) {
    var dx1 = P1[0] - V[0], dy1 = P1[1] - V[1];
    var dx2 = P2[0] - V[0], dy2 = P2[1] - V[1];
    var angle1 = Math.atan2(dy1, dx1);
    var angle2 = Math.atan2(dy2, dx2);

    // Midpoint angle — use the interior bisector direction
    var cross = dx1 * dy2 - dy1 * dx2;
    var midAngle;
    if (cross > 0) {
        // CW sweep from angle1 to angle2
        var sweep = angle2 - angle1;
        if (sweep < 0) sweep += 2 * Math.PI;
        midAngle = angle1 + sweep / 2;
    } else {
        // CCW sweep from angle1 to angle2
        var sweep = angle1 - angle2;
        if (sweep < 0) sweep += 2 * Math.PI;
        midAngle = angle2 + sweep / 2;
    }

    return [
        V[0] + offset * Math.cos(midAngle),
        V[1] + offset * Math.sin(midAngle)
    ];
}
```

### Right Angle Mark (L-shaped square) — 直角符号必须贴着构成直角的两条线

The right-angle mark is a small square in the corner of a 90° angle. Its two little strokes MUST lie **exactly along the two lines that form the right angle**, and the square must sit **inside** that angle, with its near corner **at the vertex**.

> 🟥 **HARD RULE — never hand-type the right-angle mark path.** Compute it from the vertex `V`
> and the TWO real segment endpoints (`P1`, `P2`) with `rightAngleMark()` below. If you type
> `d="M263.9,392 L271.9,375.9 L288,383.9"` by guessing, the square comes out **rotated off the
> two lines** (a valid square, but not hugging either line) — that is exactly the "直角符号标错了"
> bug: at D where BD⊥AC, the mark's arms were `(-0.445,0.896)`/`(0.896,0.445)` while the real
> lines are DB `(-0.894,0.447)` and DC `(0.447,0.894)` → the symbol pointed the wrong way.

```javascript
// Right angle mark at vertex V, between the two segments V→P1 and V→P2 (which are ⟂).
// P1 and P2 are the OTHER endpoints of the two actual lines meeting at V. Pick the P1/P2 that
// bound the specific corner you want to mark, so the square lands INSIDE that angle.
function rightAngleMark(V, P1, P2, size) {          // size ≈ 16–24 SVG units (small, fixed)
    var d1 = normalize([P1[0]-V[0], P1[1]-V[1]]);   // unit dir along the first line (away from V)
    var d2 = normalize([P2[0]-V[0], P2[1]-V[1]]);   // unit dir along the second line (away from V)
    var p1 = [V[0] + d1[0]*size, V[1] + d1[1]*size];            // a size along line 1
    var p2 = [p1[0] + d2[0]*size, p1[1] + d2[1]*size];          // far corner = V + size*(d1+d2)
    var p3 = [V[0] + d2[0]*size, V[1] + d2[1]*size];            // a size along line 2
    return 'M ' + p1[0].toFixed(1) + ',' + p1[1].toFixed(1) +
           ' L ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1) +
           ' L ' + p3[0].toFixed(1) + ',' + p3[1].toFixed(1);   // two strokes, no fill
}

function normalize(v) {
    var len = Math.sqrt(v[0]*v[0] + v[1]*v[1]);
    return [v[0]/len, v[1]/len];
}
```

**Rules that make it correct every time:**

1. **`P1`, `P2` are the real endpoints of the two lines forming the angle** — always compute
   directions from the vertex to those points; never invent an angle. If the right angle is
   `∠ABC` (vertex B), call `rightAngleMark(B, A, C, 20)`. If it's `BD ⟂ AC` at foot `D`, the two
   lines are `DB` and the line `AC` — call `rightAngleMark(D, B, C, 20)` (or `(D, B, A, 20)`) to
   mark the corner on that side.
2. **Both directions point INTO the angle** (away from V, toward the other endpoints) so the
   square sits inside the figure, not outside.
3. **`size` is small and fixed** (~16–24 units, ≪ the segment length) so the square reads as a
   corner mark, not a big box.
4. **The two lines really are perpendicular** — verify `dot(d1, d2) ≈ 0` before drawing; if it
   is not ~0, the angle is not 90° and a square mark is wrong.

**Worked example (this exact case — BD ⟂ AC at D):**
```javascript
var A=[120,80], B=[120,480], C=[320,480];   // △ABC, right angle at B
var D=[280,400];                            // foot of BD on AC (BD⟂AC verified: dot(AC,BD)=0)
// mark ∠ABC at B, between BA and BC:
var raB = rightAngleMark(B, A, C, 24);      // square hugs the vertical BA and horizontal BC
// mark the right angle BD⟂AC at D, on the C side (between DB and DC):
var raD = rightAngleMark(D, B, C, 20);      // arms parallel to DB and DC — NOT hand-typed
// <!-- GEOMETRY VERIFICATION -->
// ASSERT raB arms ∥ BA,BC:  dir(B→A)=(0,-1), dir(B→C)=(1,0), dot=0  ✓
// ASSERT raD arms ∥ DB,DC:  dir(D→B)=(-0.894,0.447), dir(D→C)=(0.447,0.894), dot=0  ✓
```
Emit each as `<path d="..." fill="none" stroke="#..." stroke-width="2.5"/>`. After writing, sanity-check that each mark's two strokes visibly run **along** the two lines at the vertex (parallel, touching the corner) — if the little square looks tilted relative to the lines, you hand-typed it; regenerate with `rightAngleMark()`.

---

## Tick Marks for Equal Segments (等长线段标记)

Equal-length hash marks are short strokes drawn **across the middle of a segment,
perpendicular to it**. On a slanted side (a triangle leg, a rhombus edge) you CANNOT
eyeball or hand-type the `x1/y1/x2/y2` — a tick that looks centered on a near-vertical
leg is actually offset ~100px to the side and **flies off the segment onto empty space**
(real bad case: the AD/AE mid-segment ticks landed outside the triangle while the DB/EC
ticks were fine). Always compute the tick from the segment's two endpoints.

**HARD RULE — never hand-write tick coordinates.** A tick's four numbers must be DERIVED
from the endpoints of the segment it marks, via the formula/generator below. If you find
yourself typing `<line id="tick-…" x1="234" y1="248" …>` by guessing, stop and compute it.
To mark a *sub-segment* (e.g. `AD` = the half of `AB` from `A` to midpoint `D`), pass the
sub-segment's own endpoints (`A` and `D`) — NOT `A` and `B`.

**Formula:** tick center = **midpoint** of the segment; the stroke runs along the
**perpendicular unit vector**, from `mid − perp·half` to `mid + perp·half`.

```
mid  = ((x1+x2)/2, (y1+y2)/2)
d    = (x2−x1, y2−y1);  L = hypot(d);  u = (d/L)          # unit vector ALONG segment
perp = (−u_y, u_x)                                        # unit vector PERPENDICULAR
half = size (≈7)                                          # tick half-length in px
tick endpoints:  (mid ± perp·half)
```

**Generator — returns a ready-to-paste `<line>` centered on the segment's midpoint:**

```javascript
// One equal-length tick across the MIDDLE of segment (x1,y1)-(x2,y2).
function tick(x1, y1, x2, y2, id, size) {
    size = size || 7;
    var mx = (x1 + x2) / 2, my = (y1 + y2) / 2;          // midpoint
    var dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1;
    var px = -dy / L, py = dx / L;                        // perpendicular unit vector
    var ax = (mx - px * size).toFixed(1), ay = (my - py * size).toFixed(1);
    var bx = (mx + px * size).toFixed(1), by = (my + py * size).toFixed(1);
    return '<line id="' + id + '" x1="' + ax + '" y1="' + ay +
           '" x2="' + bx + '" y2="' + by + '" stroke="#8b5cf6" stroke-width="3"/>';
}

// For DOUBLE ticks (second equal pair), offset each stroke ALONG the segment by ±4px:
function ticks(x1, y1, x2, y2, n, id, size) {
    size = size || 7;
    var mx=(x1+x2)/2, my=(y1+y2)/2, dx=x2-x1, dy=y2-y1, L=Math.hypot(dx,dy)||1;
    var ux=dx/L, uy=dy/L, px=-uy, py=ux, out=[];
    for (var i=0;i<n;i++){
        var o=(i-(n-1)/2)*4, cx=mx+ux*o, cy=my+uy*o;     // slide center along segment
        out.push('<line id="'+id+'-'+i+'" x1="'+(cx-px*size).toFixed(1)+'" y1="'+(cy-py*size).toFixed(1)+
                 '" x2="'+(cx+px*size).toFixed(1)+'" y2="'+(cy+py*size).toFixed(1)+'" stroke="#8b5cf6" stroke-width="3"/>');
    }
    return out.join('\n');
}
```

**Worked example (the triangle-midline case).** Triangle `A=(400,144.3)`, `B=(160,560)`,
`C=(640,560)`, midpoints `D=(280,352.2)` on `AB`, `E=(520,352.2)` on `AC`. Mark the four
equal halves `AD, DB, AE, EC`:

```javascript
tick(400,144.3, 280,352.2, "tick-ad");  // → center (340.0,248.2)  ✅ ON segment AD
tick(280,352.2, 160,560,   "tick-db");  // → center (220.0,456.1)  ✅ ON segment DB
tick(400,144.3, 520,352.2, "tick-ae");  // → center (460.0,248.2)  ✅ ON segment AE
tick(520,352.2, 640,560,   "tick-ec");  // → center (580.0,456.1)  ✅ ON segment EC
```

Note the correct centers `(340,248)` / `(460,248)` for the upper ticks — the bad case had
them hand-typed at `(240,252)` / `(560,252)`, i.e. ~100px OUTSIDE the legs. The generator
makes that impossible: the center is literally the segment midpoint.

> If you are emitting the SVG from a Python build script (common in this skill), port the
> same three lines — `mid`, `perp = (-dy/L, dx/L)`, `mid ± perp*size` — and f-string a
> `<line>`. The point is: **the four numbers come from the endpoints, never from eyeballing.**
> `scripts/check_svg_node_graph.py` / geometry gates can only see the points they're told
> about; a mis-placed decorative tick will otherwise sail through to the final video.

---

## Assertion Patterns (验证模式)

After computing all coordinates, verify EVERY constraint from the problem:

```javascript
function assertApprox(a, b, msg, eps) {
    eps = eps || 1.0;
    if (Math.abs(a - b) > eps) throw new Error(msg + ': ' + a + ' vs ' + b);
}

function dist(P1, P2) {
    return Math.sqrt((P2[0]-P1[0])**2 + (P2[1]-P1[1])**2);
}

function dotProduct(P1, P2, P3, P4) {
    return (P2[0]-P1[0])*(P4[0]-P3[0]) + (P2[1]-P1[1])*(P4[1]-P3[1]);
}

function crossProduct(P1, P2, P3, P4) {
    return (P2[0]-P1[0])*(P4[1]-P3[1]) - (P2[1]-P1[1])*(P4[0]-P3[0]);
}

// Perpendicularity: dot product = 0
assertApprox(dotProduct(A, E, E, F), 0, 'AE ⊥ EF');

// Parallelism: cross product = 0
assertApprox(crossProduct(A, B, D, C), 0, 'AB ∥ DC');

// Equal lengths
assertApprox(dist(A, B), dist(C, D), 'AB = CD');

// Length ratio
assertApprox(dist(A, E) / dist(E, F), 2.0, 'AE/EF = 2', 0.02);

// Midpoint
assertApprox(dist(E, [(A[0]+B[0])/2, (A[1]+B[1])/2]), 0, 'E is midpoint of AB');

// Point on segment: collinearity + between check
assertApprox(crossProduct(B, E, B, C), 0, 'E on line BC');
```

---

## Complete Worked Example: Rhombus ∠A = 60°

**Problem:** 菱形 ABCD 中，∠A = 60°，对角线 AC 和 BD 交于点 O。求对角线长度比。

**Step 1 — Compute coordinates:**

```javascript
// viewBox="0 0 700 500"
var cx = 350, cy = 250;
var side = 180;  // side length in SVG units

// ∠A = 60° → half of angle A at the diagonal = 30°
// Short diagonal d1 = 2 × side × sin(30°) = side
// Long diagonal d2 = 2 × side × cos(30°) = side × √3
var d1 = side;
var d2 = side * Math.sqrt(3);

// Place with long diagonal horizontal (A–C direction)
var O = [cx, cy];
var A = [cx - d2/2, cy];                 // left (60° vertex)
var C = [cx + d2/2, cy];                 // right (60° vertex)
var B = [cx, cy - d1/2];                 // top (120° vertex)
var D = [cx, cy + d1/2];                 // bottom (120° vertex)

// Computed coordinates:
// O = (350, 250)
// A = (350 - 155.9, 250) = (194.1, 250)
// C = (350 + 155.9, 250) = (505.9, 250)
// B = (350, 250 - 90) = (350, 160)
// D = (350, 250 + 90) = (350, 340)
```

**Step 2 — Assert constraints:**

```javascript
// All sides equal
assertApprox(dist(A,B), side, 'AB = side');  // √(155.9² + 90²) = 180 ✓
assertApprox(dist(B,C), side, 'BC = side');  // √(155.9² + 90²) = 180 ✓
assertApprox(dist(C,D), side, 'CD = side');
assertApprox(dist(D,A), side, 'DA = side');

// Diagonals perpendicular
assertApprox(dotProduct(A,C,B,D), 0, 'AC ⊥ BD');
// AC = (311.8, 0), BD = (0, 180) → dot = 0 ✓

// O is midpoint of both diagonals
assertApprox(dist(O, [(A[0]+C[0])/2, (A[1]+C[1])/2]), 0, 'O midpoint of AC');
assertApprox(dist(O, [(B[0]+D[0])/2, (B[1]+D[1])/2]), 0, 'O midpoint of BD');
```

**Step 3 — Angle arcs:**

```javascript
// ∠A = 60° — arc between arms AB and AD
var arcA = angleArc(A, B, D, 30);
// dx1 = 155.9, dy1 = -90; dx2 = 155.9, dy2 = 90
// cross = 155.9×90 - (-90)×155.9 = 14031 + 14031 = 28062 > 0 → sweep=1 ✓

// ∠B = 120° — arc between arms BA and BC
var arcB = angleArc(B, A, C, 30);
// dx1 = -155.9, dy1 = 90; dx2 = 155.9, dy2 = 90
// cross = (-155.9)×90 - 90×155.9 = -14031 - 14031 = -28062 < 0 → sweep=0 ✓
```

**Step 4 — SVG output:**

```html
<!-- GEOMETRY VERIFICATION
POINTS: A=(194.1,250) B=(350,160) C=(505.9,250) D=(350,340) O=(350,250)
ASSERT perpendicular A C B D
ASSERT midpoint O A C
ASSERT midpoint O B D
ASSERT ratio |AB| |BC| 1.0
-->
<svg viewBox="0 0 700 500" id="mt-g-svg">
  <!-- Rhombus sides -->
  <path d="M 194.1,250 L 350,160 L 505.9,250 L 350,340 Z"
        class="shape-primary" fill="rgba(6,182,212,0.08)"/>

  <!-- Diagonals (dashed) -->
  <line x1="194.1" y1="250" x2="505.9" y2="250"
        class="shape-derived" stroke-dasharray="8,6"/>
  <line x1="350" y1="160" x2="350" y2="340"
        class="shape-derived" stroke-dasharray="8,6"/>

  <!-- Right angle mark at O -->
  <path d="M 365,250 L 365,265 L 350,265"
        stroke="#d97706" stroke-width="2" fill="none"/>

  <!-- Angle arc ∠A = 60° (sweep=1) -->
  <path d="M 220.1,235 A 30,30 0 0,1 220.1,265"
        stroke="#d97706" stroke-width="2" fill="none"/>

  <!-- Angle arc ∠B = 120° (sweep=0) -->
  <path d="..." stroke="#d97706" stroke-width="2" fill="none"/>

  <!-- Center dot O -->
  <circle cx="350" cy="250" r="4" fill="#6366f1"/>

  <!-- Vertex labels -->
  <text x="180" y="250" class="geo-label" text-anchor="end">A</text>
  <text x="350" y="148" class="geo-label" text-anchor="middle">B</text>
  <text x="520" y="250" class="geo-label" text-anchor="start">C</text>
  <text x="350" y="360" class="geo-label" text-anchor="middle">D</text>
  <text x="360" y="270" class="geo-label">O</text>
</svg>
```

---

## Complete Worked Example: Circle with Tangent

**Problem:** ⊙O 直径 AB = 8, C 在圆上, AC = 4, 过 C 作切线 l, 过 B 作 l 的垂线 BD.

```javascript
// viewBox="0 0 700 500"
var r = 120;  // radius in SVG units (diameter 240)
var O = [300, 250];
var A = [O[0] - r, O[1]];          // (180, 250)
var B = [O[0] + r, O[1]];          // (420, 250)

// AC = 4 = AB/2 = diameter/2 = radius → triangle OAC equilateral
// ∠AOC = 60° → C at 120° from positive x (measured from O)
var angleC_deg = 120;
var angleC_rad = angleC_deg * Math.PI / 180;
var C = [O[0] + r * Math.cos(angleC_rad),
         O[1] - r * Math.sin(angleC_rad)];  // y-down in SVG
// C = (300 + 120×cos120°, 250 - 120×sin120°) = (300 - 60, 250 - 103.9) = (240, 146.1)

// Tangent at C: perpendicular to OC
var OC_vec = [C[0]-O[0], C[1]-O[1]];       // (-60, -103.9)
var tangent_dir = [OC_vec[1], -OC_vec[0]];  // (-103.9, 60) — rotated 90° CW
var tangent_len = Math.sqrt(tangent_dir[0]**2 + tangent_dir[1]**2);
var tangent_unit = [tangent_dir[0]/tangent_len, tangent_dir[1]/tangent_len];

// D: intersection of line through B perpendicular to tangent, with tangent through C
// BD direction = OC direction (perpendicular to tangent)
// Parametric BD: B + t × OC_unit
// Parametric tangent: C + s × tangent_unit
// Solve for intersection
var D = lineIntersection(
    B, [B[0] + OC_vec[0], B[1] + OC_vec[1]],
    C, [C[0] + tangent_dir[0], C[1] + tangent_dir[1]]
);

// E: BD ∩ circle (second intersection besides implicit extension)
// Solve |E - O| = r along line BD

// Assert: OC ⊥ tangent (tangent is perpendicular to radius)
assertApprox(dotProduct(O, C, C, [C[0]+tangent_dir[0], C[1]+tangent_dir[1]]), 0, 'OC ⊥ tangent');

// Assert: BD ⊥ tangent
assertApprox(dotProduct(B, D, C, [C[0]+tangent_dir[0], C[1]+tangent_dir[1]]), 0, 'BD ⊥ tangent');
```

---

## SVG Coordinate System Reminders

1. **y-axis points DOWN** in SVG — `(0,0)` is top-left
2. When computing from math coordinates, negate y: `svgY = centerY - mathY`
3. Angles: `atan2(dy, dx)` in SVG gives angles where positive = clockwise rotation on screen
4. For circle points in SVG: `x = cx + r*cos(θ)`, `y = cy + r*sin(θ)` where θ is measured in SVG convention (0 = right, positive = down)
5. To convert math angle to SVG: negate the y-component or negate the angle

---

## Label Placement & Collision Avoidance (标签排布，禁止重叠)

Vertex/point labels are placed by hand, so besides keeping each label off its own vertex
(15–25 units), you MUST keep labels from colliding with **each other**. A pre-render gate
(`scripts/check_svg_label_overlap.py`, SKILL.md Rule #28) fails the render if two `<text>`
labels in one `<svg>` overlap.

Rules:

1. **Never stack multiple labels on one shared point or short line.** The canonical bug is a
   pulley/lever diagram that puts the fulcrum label and both arm labels on the SAME horizontal
   diameter — they collide into unreadable mush.
2. **Center label above, arm labels below** (or vice-versa) so their vertical bands don't meet;
   anchor arm labels `end` on the left and `start` on the right and push them **outward past the
   shape edge**, not toward the crowded center.
3. **Keep a gap of ≥ ~1 label-height** (≥ the `font-size` in viewBox units) between any two boxes.
4. **Stagger point labels that share an axis** (e.g. `A(-3,0)` next to `E(-5,0)`): offset their
   `y`, or drop the coordinates to bare letters, so the boxes clear.
5. **Don't bury an axis tick number** under a point label — move the tick, or omit the redundant
   coordinate label.

**Worked pattern — fulcrum O with two arm labels (the correct version of the classic bug):**

```html
<!-- circle: cx=230 cy=170 r=92 ; diameter is the horizontal lever arm -->
<circle cx="230" cy="170" r="9" fill="#6366f1"/>
<!-- fulcrum label ABOVE the line, clear of the arms -->
<text x="230" y="132" text-anchor="middle" class="geo-label">支点 O</text>
<!-- arm labels BELOW the line, anchored outward, each on its own half -->
<text x="180" y="200" text-anchor="middle" class="arm-label">动力臂 r</text>
<text x="280" y="200" text-anchor="middle" class="arm-label">阻力臂 r</text>
<!-- (fulcrum band y≈114–136; arm band y≈182–204 → ≥ 1 label-height clear) -->
```

---

## Checklist for Every Geometry Scene

- [ ] All coordinates computed from problem constraints (not estimated)
- [ ] Every constraint asserted (perpendicular → dot=0, parallel → cross=0, length ratio, midpoint)
- [ ] `<!-- GEOMETRY VERIFICATION -->` block written with POINTS and ASSERTs
- [ ] Angle arcs use cross-product for sweep direction (Rule 22)
- [ ] Right angle marks use `rightAngleMark(V,P1,P2,size)` computed from the real vertex + two segment endpoints (NEVER hand-typed) — the little square's two strokes run **along the two perpendicular lines** and sit inside the angle at the vertex; verify `dot(d1,d2)≈0` (直角符号贴线、不旋转、不跑偏)
- [ ] Equal-length segments marked with tick marks **computed via `tick(x1,y1,x2,y2,…)`** from the segment's own endpoints — NEVER hand-typed coordinates (else the tick flies off a slanted leg; see *Tick Marks for Equal Segments*). For a sub-segment like `AD`, pass `A` and midpoint `D`, not `A` and `B`.
- [ ] Labels offset from vertices to avoid overlap (15–25 SVG units)
- [ ] **No label collides with another label** — no two `<text>` boxes overlap; center vs arm labels split above/below; point labels on an axis staggered (Rule #28, gate `check_svg_label_overlap.py`)
- [ ] viewBox chosen so figure is centered with ≥30 unit margin
- [ ] **Inclined plane (斜面) is right-side-up** — horizontal base at the BOTTOM (largest y), peak at the TOP; object on the upper face; normal force N points up-and-out (never downward) (Pattern 8)
- [ ] `python3 "$EDU_SKILL_ROOT/scripts/check_geometry_verification.py" dist` passes
