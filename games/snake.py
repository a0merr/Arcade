"""
Snake -- vibrant colors, clearly visible snake, Windows compatible.
"""
import random
import time

from utils.terminal import (
    put, buf_flush, get_terminal_size,
    get_key, wait_key, flush_keys,
    FG, BG, RESET, BOLD,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
)
from utils.display import draw_box, center_in_box

BOARD_W = 40
BOARD_H = 20

# Vivid colors
C_BORDER   = FG["bcyan"]
C_HEAD     = BG["bgreen"] + FG["black"]   # bright green BG for head
C_BODY     = FG["bgreen"]                  # bright green text for body
C_TAIL     = FG["green"]                   # dimmer for tail segments
C_FOOD     = BG["bred"]   + FG["bwhite"]  # red BG white text food
C_SCORE    = FG["byellow"]
C_TITLE    = FG["bwhite"]
C_DIM      = FG["white"]
C_OVER     = FG["bred"]
C_PANEL    = FG["bcyan"]

PANEL_W = 16
TOTAL_W = BOARD_W + 2 + PANEL_W

HEAD_CHARS = {(0, 1): ">>", (0,-1): "<<", (-1,0): "^^", (1,0): "vv"}
BODY_CHAR  = "##"
FOOD_CHAR  = "** "


def run(high_score=0):
    sh, sw = get_terminal_size()
    board_row = max(0, (sh - BOARD_H - 2) // 2)
    board_col = max(0, (sw - TOTAL_W) // 2)
    panel_col = board_col + BOARD_W + 2

    def place_food(snake):
        while True:
            f = (random.randint(1, BOARD_H - 2), random.randint(1, BOARD_W - 2))
            if f not in snake:
                return f

    def new_game():
        snake = [(BOARD_H // 2, BOARD_W // 2 - i) for i in range(4)]
        return snake, (0, 1), place_food([]), 0

    def draw_panel(score, speed_level, length):
        draw_box(board_row, panel_col, BOARD_H + 2, PANEL_W, "", C_PANEL)
        put(board_row + 2,  panel_col + 2, "SCORE",   C_TITLE, bold=True)
        put(board_row + 3,  panel_col + 2, f"{score:05d}", C_SCORE, bold=True)
        put(board_row + 5,  panel_col + 2, " BEST",   C_TITLE, bold=True)
        put(board_row + 6,  panel_col + 2, f"{max(score, high_score):05d}", C_SCORE)
        put(board_row + 8,  panel_col + 2, "LEVEL",   C_TITLE, bold=True)
        put(board_row + 9,  panel_col + 2, f"  {speed_level:3d}", C_SCORE)
        put(board_row + 11, panel_col + 2, "LENGTH",  C_TITLE, bold=True)
        put(board_row + 12, panel_col + 2, f"  {length:4d}", C_SCORE)
        put(board_row + 14, panel_col + 1, "WASD /",  C_DIM)
        put(board_row + 15, panel_col + 1, "ARROWS",  C_DIM)
        put(board_row + 16, panel_col + 1, "to move", C_DIM)
        put(board_row + 18, panel_col + 1, "Q quit",  C_DIM)

    def draw_full(snake, food, score, speed_level, direction):
        # Board
        draw_box(board_row, board_col, BOARD_H + 2, BOARD_W + 2, "SNAKE", C_BORDER)

        # Food — red block, stands out
        fy, fx = food
        put(board_row + fy, board_col + 1 + fx, "@", C_FOOD, bold=True)

        # Snake body (back to front so head draws last)
        for i in range(len(snake) - 1, -1, -1):
            sy, sx = snake[i]
            if i == 0:
                hch = HEAD_CHARS.get(direction, "OO")
                put(board_row + sy, board_col + 1 + sx, hch, C_HEAD, bold=True)
            elif i < 4:
                put(board_row + sy, board_col + 1 + sx, BODY_CHAR, C_BODY, bold=True)
            else:
                put(board_row + sy, board_col + 1 + sx, "oo", C_TAIL)

        draw_panel(score, speed_level, len(snake))
        buf_flush()

    snake, direction, food, score = new_game()
    speed_level = 1
    flush_keys()
    draw_full(snake, food, score, speed_level, direction)

    while True:
        delay = max(0.04, 0.14 - (speed_level - 1) * 0.01)

        t0 = time.time()
        key = None
        while time.time() - t0 < delay:
            k = get_key()
            if k is not None:
                key = k
                break
            time.sleep(0.01)

        dy, dx = direction
        if   key in (KEY_UP,    'w') and dy != 1:  direction = (-1, 0)
        elif key in (KEY_DOWN,  's') and dy != -1: direction = (1,  0)
        elif key in (KEY_LEFT,  'a') and dx != 1:  direction = (0, -1)
        elif key in (KEY_RIGHT, 'd') and dx != -1: direction = (0,  1)
        elif key == 'q':
            return score

        dy, dx = direction
        head = (snake[0][0] + dy, snake[0][1] + dx)

        # Collision
        if not (1 <= head[0] <= BOARD_H - 1 and 1 <= head[1] <= BOARD_W - 1) or head in snake:
            result = _game_over(board_row, board_col, BOARD_W + 2, BOARD_H + 2, score, high_score)
            if result == 'restart':
                for sy in range(1, BOARD_H + 1):
                    put(board_row + sy, board_col + 1, "  " * BOARD_W)
                buf_flush()
                snake, direction, food, score = new_game()
                speed_level = 1
                flush_keys()
                draw_full(snake, food, score, speed_level, direction)
                continue
            return score

        tail = snake[-1]
        snake.insert(0, head)

        if head == food:
            score += 10 + speed_level
            speed_level = 1 + score // 50
            food = place_food(snake)
            # Full redraw on food eat to update length
            draw_full(snake, food, score, speed_level, direction)
        else:
            snake.pop()
            # Erase tail
            put(board_row + tail[0], board_col + 1 + tail[1], "  ")
            # Redraw head and neck only
            for i in range(min(5, len(snake))):
                sy, sx = snake[i]
                if i == 0:
                    hch = HEAD_CHARS.get(direction, "OO")
                    put(board_row + sy, board_col + 1 + sx, hch, C_HEAD, bold=True)
                elif i < 4:
                    put(board_row + sy, board_col + 1 + sx, BODY_CHAR, C_BODY, bold=True)
                else:
                    put(board_row + sy, board_col + 1 + sx, "oo", C_TAIL)
            draw_panel(score, speed_level, len(snake))
            buf_flush()


def _game_over(board_row, board_col, box_w, box_h, score, high_score):
    ow, oh = 28, 9
    or_ = board_row + (box_h - oh) // 2
    oc  = board_col + (box_w - ow) // 2
    draw_box(or_, oc, oh, ow, "GAME OVER", C_OVER)
    put(or_ + 2, oc + 2, f"  SCORE : {score:05d}",                  C_OVER,  bold=True)
    put(or_ + 3, oc + 2, f"   BEST : {max(score, high_score):05d}", C_SCORE, bold=True)
    center_in_box(or_, oc, ow, 5, "[R] Restart", C_DIM)
    center_in_box(or_, oc, ow, 6, "[Q] Quit",    C_DIM)
    buf_flush()
    flush_keys()
    while True:
        k = wait_key()
        if k == 'r': return 'restart'
        if k == 'q': return 'quit'