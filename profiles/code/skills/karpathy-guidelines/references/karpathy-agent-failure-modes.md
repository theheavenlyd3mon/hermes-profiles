# Karpathy's Three Agent Failure Modes — Original Quotes

Source: https://x.com/karpathy/status/2015883857489522876

## 1. Silent Assumptions

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

## 2. Overengineering

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

## 3. Collateral Edits

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

## Root Cause: Jagged Intelligence

Karpathy's "ghosts vs animals" framing: LLMs aren't brains optimized for survival — they're ghosts optimized for imitating text and collecting puzzle rewards. Result: genius polymath and confused grade-schooler simultaneously. Standard RL improves everything verifiable (code, tests) but not softer skills (knowing when to ask, judging importance).

Your job as an operator: catch the 10-year-old mistakes before they compound. Let the PhD-level reasoning run.
