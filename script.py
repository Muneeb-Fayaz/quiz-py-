#!/usr/bin/env python3
"""
BRAIN ARENA - a smart quiz game (pure Python, no dependencies)

What makes it "smart":
  * Adaptive difficulty: answer right and questions get harder, miss and they ease off.
  * Speed bonus: the faster you answer, the more points you earn.
  * Streak multiplier: chain correct answers for up to 2x points.
  * Lifelines: one 50/50 and one Skip per game.
  * Leaderboard saved to quiz_scores.json, plus a per-category skill report at the end.

Run:  python quiz_game.py
"""

import json
import random
import sys
import time
from pathlib import Path

QUESTION_TIME = 15          # seconds per question (for the speed bonus / time-out)
MAX_ROUNDS = 10
SCORE_FILE = Path(__file__).with_name("quiz_scores.json")

# ---- ANSI colours (auto-disabled if the terminal is not a TTY) -------------
USE_COLOR = sys.stdout.isatty()


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


GREEN, RED, YELLOW, CYAN, BOLD, DIM = "92", "91", "93", "96", "1", "2"

# ---- Question bank: (question, correct answer, [wrong answers], difficulty 1-3)
BANK = {
    "Science": [
        ("Which planet is known as the Red Planet?", "Mars", ["Venus", "Jupiter", "Mercury"], 1),
        ("What is the powerhouse of the cell?", "Mitochondria", ["Nucleus", "Ribosome", "Golgi body"], 1),
        ("What is the chemical symbol for gold?", "Au", ["Ag", "Gd", "Go"], 2),
        ("Which gas makes up most of Earth's atmosphere?", "Nitrogen", ["Oxygen", "Carbon dioxide", "Argon"], 2),
        ("Which blood type is the universal red-cell donor?", "O negative", ["AB positive", "A negative", "B positive"], 3),
        ("The Higgs boson is associated with giving particles what?", "Mass", ["Charge", "Spin", "Colour"], 3),
    ],
    "Python & Tech": [
        ("Which keyword defines a function in Python?", "def", ["func", "function", "define"], 1),
        ("What does len([1, 2, 3]) return?", "3", ["2", "4", "1"], 1),
        ("What type does 3 / 2 produce in Python 3?", "float", ["int", "decimal", "double"], 2),
        ("Which of these built-in types is immutable?", "tuple", ["list", "dict", "set"], 2),
        ("What is the time complexity of binary search?", "O(log n)", ["O(n)", "O(1)", "O(n log n)"], 3),
        ("In CPython, what does GIL stand for?", "Global Interpreter Lock",
         ["General Interface Layer", "Global Instruction Loop", "Guarded Iterator Lock"], 3),
    ],
    "Geography": [
        ("What is the capital of Japan?", "Tokyo", ["Kyoto", "Osaka", "Seoul"], 1),
        ("On which continent is the Sahara Desert?", "Africa", ["Asia", "South America", "Australia"], 1),
        ("What is the capital of Australia?", "Canberra", ["Sydney", "Melbourne", "Perth"], 2),
        ("What is the smallest country in the world by area?", "Vatican City", ["Monaco", "San Marino", "Malta"], 2),
        ("Which country has the most time zones, counting overseas territories?", "France",
         ["Russia", "United States", "United Kingdom"], 3),
        ("Which is the deepest lake in the world?", "Lake Baikal", ["Lake Superior", "Lake Victoria", "Lake Tanganyika"], 3),
    ],
    "History": [
        ("Who was the first President of the United States?", "George Washington",
         ["Thomas Jefferson", "John Adams", "Abraham Lincoln"], 1),
        ("In which year did World War II end?", "1945", ["1939", "1918", "1950"], 1),
        ("Which civilisation built Machu Picchu?", "Inca", ["Aztec", "Maya", "Olmec"], 2),
        ("Who was independent India's first Prime Minister?", "Jawaharlal Nehru",
         ["Sardar Patel", "Lal Bahadur Shastri", "Mahatma Gandhi"], 2),
        ("In which year was the Magna Carta sealed?", "1215", ["1066", "1348", "1492"], 3),
        ("Which of the ancient Seven Wonders stood in Alexandria?", "The Lighthouse (Pharos)",
         ["Hanging Gardens", "Colossus", "Temple of Artemis"], 3),
    ],
    "Sports & Fun": [
        ("How many players per side are on the field in football (soccer)?", "11", ["9", "10", "12"], 1),
        ("Which sport uses a shuttlecock?", "Badminton", ["Tennis", "Squash", "Table tennis"], 1),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci", ["Michelangelo", "Raphael", "Botticelli"], 2),
        ("Which chess piece can only move diagonally?", "Bishop", ["Rook", "Knight", "Pawn"], 2),
        ("Which country won the 2011 Cricket World Cup?", "India", ["Sri Lanka", "Australia", "Pakistan"], 2),
        ("Which language has the most native speakers worldwide?", "Mandarin Chinese",
         ["English", "Spanish", "Hindi"], 3),
    ],
}

RANKS = [
    (0, "Curious Newcomer"),
    (800, "Quick Thinker"),
    (1600, "Brainiac"),
    (2400, "Quiz Master"),
    (3200, "Grandmaster of Trivia"),
]


# ---- Helpers ---------------------------------------------------------------
def stars(d):
    return "★" * d + "☆" * (3 - d)


def build_pool(choice):
    pool = []
    for cat, items in BANK.items():
        if choice in ("Mixed", cat):
            for q, right, wrong, diff in items:
                pool.append({"cat": cat, "q": q, "right": right, "wrong": wrong, "diff": diff})
    return pool


def pick_question(pool, used, level):
    """Choose the unused question whose difficulty is closest to the player's level."""
    candidates = [q for q in pool if id(q) not in used]
    if not candidates:
        return None
    candidates.sort(key=lambda q: (abs(q["diff"] - level), random.random()))
    return candidates[0]


def choose_category():
    cats = list(BANK) + ["Mixed"]
    print(c("\nChoose a category:", BOLD))
    for i, name in enumerate(cats, 1):
        print(f"  {i}. {name}")
    while True:
        raw = input("Pick a number (default = Mixed): ").strip()
        if raw == "":
            return "Mixed"
        if raw.isdigit() and 1 <= int(raw) <= len(cats):
            return cats[int(raw) - 1]
        print("  Please enter a valid number.")


def load_scores():
    try:
        return json.loads(SCORE_FILE.read_text())
    except (OSError, ValueError):
        return []


def save_score(name, score, category):
    scores = load_scores()
    scores.append({"name": name, "score": score, "category": category,
                   "date": time.strftime("%Y-%m-%d")})
    scores = sorted(scores, key=lambda s: s["score"], reverse=True)[:5]
    try:
        SCORE_FILE.write_text(json.dumps(scores, indent=2))
    except OSError:
        pass
    return scores


def show_leaderboard(scores):
    print(c("\n🏆 LEADERBOARD", BOLD))
    if not scores:
        print("  No scores yet - be the first!")
    for i, s in enumerate(scores, 1):
        print(f"  {i}. {s['name']:<12} {s['score']:>5}  ({s['category']}, {s['date']})")


def rank_for(score):
    title = RANKS[0][1]
    for threshold, name in RANKS:
        if score >= threshold:
            title = name
    return title


# ---- Core game -------------------------------------------------------------
def play():
    category = choose_category()
    pool = build_pool(category)
    rounds = min(MAX_ROUNDS, len(pool))

    score, streak, best_streak = 0, 0, 0
    level = 2.0                       # adaptive difficulty (1.0 - 3.0)
    lifelines = {"f": True, "s": True}
    used = set()
    stats = {}                        # category -> [correct, asked]

    print(c(f"\nGame on! {rounds} questions, {QUESTION_TIME}s each. "
            "Difficulty adapts to how you play.", CYAN))
    print(c("Lifelines: F = 50/50, S = Skip (one of each).\n", DIM))

    asked = 0
    while asked < rounds:
        q = pick_question(pool, used, level)
        if q is None:
            break
        used.add(id(q))

        options = [q["right"]] + q["wrong"]
        random.shuffle(options)
        hidden = set()

        def show():
            print(c(f"\nQ{asked + 1}/{rounds}  [{q['cat']}]  {stars(q['diff'])}"
                    f"   Score: {score}   Streak: {streak}🔥", BOLD))
            print(q["q"])
            for i, opt in enumerate(options):
                if opt in hidden:
                    print(c(f"  {'ABCD'[i]}) ---", DIM))
                else:
                    print(f"  {'ABCD'[i]}) {opt}")

        show()
        start = time.time()
        used_fifty = False
        skipped = False
        answer = None

        while True:
            hint = "Answer (A-D"
            hint += ", F=50/50" if lifelines["f"] and not used_fifty else ""
            hint += ", S=skip" if lifelines["s"] else ""
            raw = input(f"{hint}): ").strip().lower()

            if raw in ("a", "b", "c", "d"):
                idx = "abcd".index(raw)
                if idx < len(options) and options[idx] not in hidden:
                    answer = options[idx]
                    break
                print("  That option isn't available.")
            elif raw == "f" and lifelines["f"] and not used_fifty:
                lifelines["f"] = False
                used_fifty = True
                hidden = set(random.sample(q["wrong"], 2))
                show()
            elif raw == "s" and lifelines["s"]:
                lifelines["s"] = False
                skipped = True
                break
            elif raw == "q":
                print("Thanks for playing!")
                return
            else:
                print("  Invalid input.")

        if skipped:
            print(c("⏭  Skipped - here comes a new question.", YELLOW))
            continue

        elapsed = time.time() - start
        asked += 1
        stats.setdefault(q["cat"], [0, 0])[1] += 1

        if elapsed > QUESTION_TIME:
            print(c(f"⏰ Too slow ({elapsed:.1f}s)! The answer was: {q['right']}", RED))
            streak = 0
            level = max(1.0, level - 0.5)
        elif answer == q["right"]:
            streak += 1
            best_streak = max(best_streak, streak)
            base = 100 * q["diff"] // (2 if used_fifty else 1)
            speed = int(50 * (QUESTION_TIME - elapsed) / QUESTION_TIME)
            mult = 1 + 0.25 * min(streak - 1, 4)
            gained = int((base + speed) * mult)
            score += gained
            level = min(3.0, level + 0.5)
            stats[q["cat"]][0] += 1
            print(c(f"✅ Correct! +{gained} pts  (base {base}, speed +{speed}, x{mult:.2f})", GREEN))
        else:
            streak = 0
            level = max(1.0, level - 0.7)
            print(c(f"❌ Nope. The answer was: {q['right']}", RED))

    # ---- Results -----------------------------------------------------------
    print(c("\n" + "=" * 44, BOLD))
    print(c(f" FINAL SCORE: {score}", BOLD))
    print(c(f" Rank: {rank_for(score)}   |   Best streak: {best_streak}🔥", CYAN))
    print(c("=" * 44, BOLD))

    print("\nSkill report:")
    for cat, (right, total) in stats.items():
        bar = "█" * right + "░" * (total - right)
        print(f"  {cat:<14} {bar} {right}/{total}")

    name = input("\nEnter your name for the leaderboard: ").strip()[:12] or "Player"
    show_leaderboard(save_score(name, score, category))


def main():
    print(c("\n🧠  BRAIN ARENA - the quiz that adapts to you  🧠", BOLD))
    show_leaderboard(load_scores())
    try:
        while True:
            play()
            if input("\nPlay again? (y/n): ").strip().lower() != "y":
                break
    except (EOFError, KeyboardInterrupt):
        pass
    print("\nSee you next time! 👋")


if __name__ == "__main__":
    main()