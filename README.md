<div align="center">

# 🧠 Brain Arena

### *The quiz game that adapts to you.*

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-blue)

**A terminal trivia game with adaptive difficulty, speed bonuses, streak multipliers, lifelines and a saved leaderboard, all in one Python file.**

</div>

---

## ✨ Features

| | Feature | What it does |
|---|---|---|
| 🎯 | **Adaptive difficulty** | Answer right and questions get harder (★★★). Miss and they ease off. |
| ⚡ | **Speed bonus** | The faster you answer, the more points you earn. |
| 🔥 | **Streak multiplier** | Chain correct answers for up to **2x** points. |
| 🛟 | **Lifelines** | One **50/50** and one **Skip** per game. Use them wisely. |
| ⏱️ | **Time limit** | 15 seconds per question. Answer too late and you score nothing. |
| 📚 | **5 categories + Mixed** | Science, Python & Tech, Geography, History, Sports & Fun. |
| 📊 | **Skill report** | See how you did in each category at the end of the game. |
| 🏆 | **Leaderboard** | Your top 5 scores are saved locally between games. |
| 🎖️ | **Rank titles** | Climb from *Curious Newcomer* to *Grandmaster of Trivia*. |

---

## 🚀 Quick Start

No installs needed. Just Python 3.8 or newer.

```bash
python quiz_game.py
```

On macOS or Linux you may need `python3 quiz_game.py`.

---

## 🎮 How to Play

1. **Pick a category** by number, or press Enter for *Mixed*.
2. **Read the question** and its four options (A–D).
3. **Type your answer** and press Enter.

| Key | Action |
|-----|--------|
| `A` `B` `C` `D` | Choose an answer |
| `F` | Use the **50/50** lifeline (removes two wrong options, halves the base points) |
| `S` | **Skip** the question and get a new one (no penalty) |
| `Q` | Quit the game |

### Example round

```text
Q3/6  [Python & Tech]  ★★☆   Score: 240   Streak: 2🔥
Which of these built-in types is immutable?
  A) list
  B) dict
  C) set
  D) tuple
Answer (A-D, F=50/50, S=skip): d
✅ Correct! +277 pts  (base 200, speed +39, x1.25)
```

---

## 🧮 Scoring

```text
points = (base + speed bonus) × streak multiplier
```

| Part | Formula |
|------|---------|
| **Base** | `100 × difficulty` (1–3 stars), halved if you used 50/50 |
| **Speed bonus** | Up to `+50`, shrinking linearly over the 15-second limit |
| **Streak multiplier** | `1 + 0.25 × (streak − 1)`, capped at **2.0x** |

### 🎖️ Ranks

| Score | Title |
|-------|-------|
| 0+ | Curious Newcomer |
| 800+ | Quick Thinker |
| 1600+ | Brainiac |
| 2400+ | Quiz Master |
| 3200+ | Grandmaster of Trivia |

---

## 🛠️ Customize It

Everything lives in `quiz_game.py`, and the settings are at the top of the file:

```python
QUESTION_TIME = 15   # seconds per question
MAX_ROUNDS = 10      # questions per game
```

### Add your own questions

Add entries to the `BANK` dictionary in this format:
`(question, correct answer, [wrong answers], difficulty 1-3)`

```python
"Movies": [
    ("Who directed Inception?", "Christopher Nolan",
     ["Steven Spielberg", "James Cameron", "Ridley Scott"], 2),
],
```

A new category shows up in the menu automatically. Give each category at least 6 questions so a full game and skips work smoothly.

---

## 📁 Project Structure

```text
.
├── quiz_game.py       # the whole game
├── quiz_scores.json   # created automatically after your first game
└── README.md
```

---

## 🗺️ Ideas for Next Steps

- [ ] Live countdown timer
- [ ] Two-player mode
- [ ] Load questions from a JSON/CSV file or the Open Trivia API
- [ ] Daily challenge mode

---

<div align="center">

Made with 🐍 and a lot of trivia. Have fun and beat your high score!

</div>
