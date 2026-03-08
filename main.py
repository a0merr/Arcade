#!/usr/bin/env python3
"""
Terminal Arcade -- Windows PowerShell & Unix compatible.
Run with:  python main.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.terminal import (
    init_screen, deinit_screen, start_input, stop_input,
    put, buf_flush, get_terminal_size,
    get_key, wait_key, flush_keys,
    FG, KEY_UP, KEY_DOWN, KEY_ENTER, KEY_SPACE,
)
from utils.display import draw_box, center_text, ARCADE_LOGO
from games import snake, tetris

SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".high_scores.json")

GAMES = [
    {"name": "SNAKE",  "desc": "Eat, grow, survive", "module": snake},
    {"name": "TETRIS", "desc": "Stack the blocks",   "module": tetris},
]

C_TITLE  = FG["bwhite"]
C_BORDER = FG["bcyan"]
C_SEL    = FG["byellow"]
C_NORM   = FG["cyan"]
C_DIM    = FG["white"]
C_SCORE  = FG["byellow"]

def load_scores():
    try:
        with open(SCORES_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_scores(scores):
    try:
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f)
    except Exception:
        pass


def draw_menu(selected, scores):
    sh, sw = get_terminal_size()

    logo_start = max(1, (sh - len(ARCADE_LOGO) - len(GAMES) * 2 - 10) // 2)
    for i, line in enumerate(ARCADE_LOGO):
        col = max(0, (sw - len(line)) // 2)
        put(logo_start + i, col, line, C_TITLE, bold=True)

    y = logo_start + len(ARCADE_LOGO) + 1
    center_text(y, "~ INSERT COIN ~", C_BORDER, bold=True)
    y += 2

    for i, game in enumerate(GAMES):
        hs = scores.get(game["name"], 0)
        label  = f"  {game['name']:<10}  {game['desc']:<22}  HI: {hs:06d}  "
        prefix = ">" if i == selected else " "
        line   = f"{prefix} {label} {prefix}"
        if i == selected:
            center_text(y + i * 2, line, C_SEL, bold=True)
        else:
            center_text(y + i * 2, line, C_NORM)

    y += len(GAMES) * 2 + 1
    center_text(y,     "W/S or UP/DOWN : navigate", C_DIM)
    center_text(y + 1, "  ENTER/SPACE  : play    ", C_DIM)
    center_text(y + 2, "      Q        : quit    ", C_DIM)
    buf_flush()


def check_size():
    sh, sw = get_terminal_size()
    MIN_H, MIN_W = 26, 72
    if sh < MIN_H or sw < MIN_W:
        put(sh // 2 - 1, 0, f"Terminal too small! Need {MIN_W}x{MIN_H}, got {sw}x{sh}.", FG["bred"], bold=True)
        buf_flush()
        return False
    return True


def main():
    scores  = load_scores()
    selected = 0

    init_screen()
    start_input()

    try:
        while True:
            sh, sw = get_terminal_size()
            # Clear screen each menu redraw
            for r in range(sh):
                put(r, 0, " " * sw)

            if not check_size():
                wait_key()
                continue

            draw_menu(selected, scores)

            key = wait_key()

            if key == 'q':
                break
            elif key in (KEY_UP, 'w'):
                selected = (selected - 1) % len(GAMES)
            elif key in (KEY_DOWN, 's'):
                selected = (selected + 1) % len(GAMES)
            elif key in (KEY_ENTER, KEY_SPACE, '\r', '\n'):
                game = GAMES[selected]
                hs   = scores.get(game["name"], 0)
                # Clear screen before game
                for r in range(sh):
                    put(r, 0, " " * sw)
                buf_flush()
                flush_keys()

                result = game["module"].run(high_score=hs)

                if isinstance(result, int) and result > hs:
                    scores[game["name"]] = result
                    save_scores(scores)

                flush_keys()

    finally:
        stop_input()
        deinit_screen()

    print("\nThanks for playing Terminal Arcade!  :)")


if __name__ == "__main__":
    main()
