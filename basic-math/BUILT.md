# BUILT.md — Elise & Erik Math Game

## What Was Built

A fun, interactive math training game built with **Python** and **Pygame** to help kids (and adults!) practice the four basic math operations while earning virtual money.

### Features

- **4 Operations:** Addition (+), Subtraction (−), Multiplication (×), Division (÷)
- **3 Difficulty Levels:**
  - **Level 1 (Easy):** Single-digit operands (1–9)
  - **Level 2 (Medium):** One double-digit operand (10–50) and one single-digit (2–9)
  - **Level 3 (Hard):** Double-digit operands (10–99)
- **Virtual Money System:**
  - Correct answer: **+$0.05**
  - Wrong answer: **−$0.01**
  - Timer penalty: **−$0.01 every 5 seconds** (keeps the pressure on!)
  - Money carries over between rounds — go back to the menu and switch operations without losing your balance
- **5 Tries Per Question:** No answer is revealed until you've used all 5 attempts, then a new question appears
- **Streak Tracking:** Current streak and best streak displayed
- **Progress Bar:** Level-up every 10 solved problems
- **Menu Navigation:** Click-based menus for operation and difficulty selection, with a "< Menu" button to return anytime

### Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3 |
| Graphics | Pygame |
| Window | Resizable, maximized windowed mode |

---

## How to Run

```bash
./start.sh
```

Or directly:

```bash
python3 division_game.py
```

---

## How to Improve It

### Easy Wins

1. **Sound effects** — Add a `pygame.mixer` coin sound on correct answers and a buzzer on wrong ones. Huge impact on fun factor with just a few lines.

2. **High score persistence** — Save money and best streak to a JSON file so progress isn't lost when the game closes:
   ```python
   import json
   with open("save.json", "w") as f:
       json.dump({"money": money, "best_streak": best_streak}, f)
   ```

3. **Keyboard shortcuts in menus** — Let players press `1`, `2`, `3`, `4` to pick operations and levels instead of only clicking.

4. **Visual feedback on correct/wrong** — Flash the card green or red briefly (just change the card color for ~15 frames).

5. **Configurable timer** — Let the player choose timer speed (relaxed = 10s, normal = 5s, intense = 3s) or disable it entirely.

### Medium Effort

6. **Player profiles** — Support multiple players with separate save files. Add a name-entry screen at launch.

7. **Mixed mode** — A mode that randomly picks the operation each question, testing all four skills together.

8. **Animated rewards** — Bring back particle effects (the code had them before) as an optional toggle.

9. **Statistics dashboard** — Track accuracy per operation and level. Show a bar chart of strengths and weaknesses.

10. **Timed challenge mode** — Answer as many as possible in 60 seconds. Leaderboard style.

### Bigger Projects

11. **Multiplayer** — Two players alternate turns. Whoever has more money after 20 questions wins. Could use split-screen or turn-based.

12. **Story mode** — A sequence of themed levels with increasing difficulty (e.g., "Space Mission", "Treasure Hunt"), unlocking the next after earning enough money.

13. **Web version** — Port to a browser game using Pyodide or rewrite in JavaScript with Canvas.

---

## Tips & Tricks

### For Players

- **Tab into division** — Division on Level 3 is the hardest because the dividends get large. Start with Level 1 to build speed.
- **Use elimination** — If you're not sure, estimate. For `84 / 7`, think "7 × 10 = 70, 7 × 12 = 84", so the answer is 12.
- **Watch the timer** — The countdown in the bottom-right turns **red** under 2 seconds. Don't let it tick over if you're close!
- **Build streaks** — Streaking is the fastest way to earn money. $0.05 per correct answer adds up fast if you keep the streak alive.
- **Don't guess randomly** — Wrong answers cost $0.01 each. Better to take a moment and get it right than to burn through all 5 tries.

### For Developers

- **Pygame event loop pattern** — Buttons are drawn each frame, but click detection uses the rects from the *previous* frame. This is the standard pattern because events fire before drawing.
- **Money uses `round()`** — Floating-point arithmetic can cause `0.05 - 0.01 = 0.03999...`. Always `round(value, 2)` when doing money math.
- **`clock.tick(30)` returns delta time** — The return value is milliseconds since last frame, used for the timer. No need for a separate timer module.
- **Division generates clean problems** — The dividend is always `divisor × answer`, guaranteeing whole-number results. Never show impossible problems.
- **Subtraction enforces `a ≥ b`** — A simple swap ensures no negative answers, keeping it kid-friendly.

---

## File Structure

```
division/
├── division_game.py   # Main game (all logic in one file)
├── start.sh           # Launch script
└── BUILT.md           # This file
```
