# Step 2: Teaching Script

Write the Chinese narration script for the tutorial video. Read the general narration reference from the hyperframes skill for pacing principles.

## Chinese Pacing

- **3.5-4.0 Chinese characters per second** for clear educational delivery
- 30s = ~105-120 characters
- 60s = ~210-240 characters
- Leave **0.5-1.0s silence** between steps for visual breathing
- The script should feel SHORTER than the video duration
- **Short sentences (短句，避免字幕过长).** Keep each spoken sentence ≤ ~22 Chinese characters and end it at a natural pause (`。`/`；`/`，`). Each sentence becomes one subtitle cue, and a short sentence = one clean single-line caption; long run-on sentences force the subtitle to wrap or run off the frame edge. Break a long idea into two short consecutive sentences rather than one long one.

## Script Structure

Write `SCRIPT.md` with scene markers (`---`) between sections:

```markdown
# Teaching Script

## 开场引入 (3-5s)
今天我们来看一道二次方程的求解问题。

---

## 题目朗读 (5-10s)
题目要求我们：解方程 x的平方 减 5x 加 6 等于 0。

---

## 思路分析 (5-10s)
我们观察到，这是一个标准的一元二次方程。
我们可以尝试用因式分解法来求解。

---

## 解题步骤一 (8-12s)
首先，我们需要找到两个数，它们的乘积等于6，
而且它们的和等于5。

---

## 解题步骤二 (8-12s)
经过分析，这两个数是2和3。
因此，原方程可以分解为 x减2 乘以 x减3 等于0。

---

## 解题步骤三 (6-10s)
根据零乘积原理，x减2等于0 或者 x减3等于0。
解得 x等于2 或者 x等于3。

---

## 结论总结 (5-8s)
因此，方程的两个解分别是 x等于2 和 x等于3。
这道题的关键在于熟练掌握因式分解的方法。
```

## Math Symbol Pronunciation Table

TTS reads text literally. Write what you want the voice to say:

| Symbol | Speak as | Example |
|--------|----------|---------|
| x^2 / x² | x的平方 | "x的平方 减 5x" |
| x^3 / x³ | x的立方 | "x的立方" |
| x^n | x的n次方 | "x的n次方" |
| sqrt(x) / √x | 根号x | "根号二" |
| a/b | b分之a | "2分之1" (Chinese reads denominator first) |
| pi / π | 派 | "派" |
| >= / ≥ | 大于等于 | "大于等于零" |
| <= / ≤ | 小于等于 | "小于等于五" |
| != / ≠ | 不等于 | "不等于零" |
| +/- / ± | 正负 | "正负根号五" |
| infinity / ∞ | 无穷大 | "趋向于无穷大" |
| f(x) | f x | "f x 等于" |
| f'(x) | f x 的导数 | "f x 的导数" |
| integral | 积分 | "对 x 从0到1积分" |
| lim | 极限 | "当x趋向于0时的极限" |
| log | 对数 | "以2为底的对数" |
| sin/cos/tan | 正弦/余弦/正切 | "正弦x" |
| |x| | x的绝对值 | "x的绝对值" |
| sum / Σ | 求和 | "对i从1到n求和" |
| angle / ∠ | 角 | "角ABC" |
| triangle / △ | 三角形 | "三角形ABC" |
| parallel / ∥ | 平行于 | "平行于BC" |
| perpendicular / ⊥ | 垂直于 | "垂直于BC" |

## Tone Guidance

- **Patient and clear.** Not robotic, not rushed.
- **Use transitions:** "接下来", "然后我们", "现在", "注意这里"
- **Encourage:** "我们可以发现", "不难看出", "由此可得"
- **Conclude with insight:** "这道题的关键在于...", "需要注意的是..."

## Gate

Before proceeding to Step 3:
- [ ] `SCRIPT.md` exists with `---` scene markers
- [ ] All math symbols converted to spoken Chinese using the pronunciation table
- [ ] Character count per section matches target pacing
- [ ] Script reads naturally when spoken aloud
