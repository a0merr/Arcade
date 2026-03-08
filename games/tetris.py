"""
Tetris -- vibrant colors, clearly visible falling piece, Windows compatible.
"""
import random
import time

from utils.terminal import (
    put, buf_flush, get_terminal_size,
    get_key, wait_key, flush_keys,
    FG, BG, RESET, BOLD,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE,
    PIECE_COLORS,
)
from utils.display import draw_box, center_in_box

BOARD_W  = 10
BOARD_H  = 20
CELL     = "[]"   # active/locked piece
GHOST_CH = ".."   # ghost piece
EMPTY    = "  "

TETROMINOES = {
    'I': [[(0,0),(0,1),(0,2),(0,3)], [(0,0),(1,0),(2,0),(3,0)]],
    'O': [[(0,0),(0,1),(1,0),(1,1)]],
    'T': [[(0,1),(1,0),(1,1),(1,2)], [(0,0),(1,0),(2,0),(1,1)],
          [(1,0),(1,1),(1,2),(0,1)], [(0,1),(1,1),(2,1),(1,0)]],
    'S': [[(0,1),(0,2),(1,0),(1,1)], [(0,0),(1,0),(1,1),(2,1)]],
    'Z': [[(0,0),(0,1),(1,1),(1,2)], [(0,1),(1,0),(1,1),(2,0)]],
    'J': [[(0,0),(1,0),(1,1),(1,2)], [(0,0),(0,1),(1,0),(2,0)],
          [(1,0),(1,1),(1,2),(0,2)], [(0,1),(1,1),(2,0),(2,1)]],
    'L': [[(0,2),(1,0),(1,1),(1,2)], [(0,0),(1,0),(2,0),(2,1)],
          [(1,0),(1,1),(1,2),(0,0)], [(0,0),(0,1),(1,1),(2,1)]],
}
PIECE_ORDER = list(TETROMINOES.keys())
LINE_SCORES = [0, 100, 300, 500, 800]

# Panel colors
C_BORDER  = FG["cyan"]
C_TITLE   = FG["bwhite"]
C_SCORE   = FG["byellow"]
C_DIM     = FG["white"]
C_OVER    = FG["bred"]
C_FLASH   = FG["bwhite"]

PANEL_W  = 18
BOARD_PX = BOARD_W * 2 + 2
TOTAL_W  = BOARD_PX + PANEL_W

PIECE_NAMES = {
    'I': "I-PIECE", 'O': "O-PIECE", 'T': "T-PIECE",
    'S': "S-PIECE", 'Z': "Z-PIECE", 'J': "J-PIECE", 'L': "L-PIECE",
}

def _cells(piece):
    rots = TETROMINOES[piece['kind']]
    rot  = piece['rot'] % len(rots)
    return [(piece['row'] + r, piece['col'] + c) for r, c in rots[rot]]

def _valid(board, cells):
    for r, c in cells:
        if r < 0 or r >= BOARD_H or c < 0 or c >= BOARD_W: return False
        if board[r][c] is not None: return False
    return True

def _ghost_row(board, piece):
    p = dict(piece)
    while True:
        p2 = dict(p); p2['row'] += 1
        if not _valid(board, _cells(p2)): break
        p = p2
    return p['row']

def _lock(board, piece):
    for r, c in _cells(piece):
        if 0 <= r < BOARD_H:
            board[r][c] = piece['kind']
    new_board = [row for row in board if not all(cell is not None for cell in row)]
    lines = BOARD_H - len(new_board)
    while len(new_board) < BOARD_H:
        new_board.insert(0, [None] * BOARD_W)
    return new_board, lines

def run(high_score=0):
    sh, sw = get_terminal_size()
    board_row = max(0, (sh - BOARD_H - 2) // 2)
    board_col = max(0, (sw - TOTAL_W) // 2)
    panel_col = board_col + BOARD_PX

    bag = []

    def next_piece():
        nonlocal bag
        if not bag:
            bag = PIECE_ORDER[:]
            random.shuffle(bag)
        kind = bag.pop()
        return {'kind': kind, 'rot': 0, 'row': 0, 'col': BOARD_W // 2 - 1}

    def new_game():
        nonlocal bag
        bag = []
        board = [[None] * BOARD_W for _ in range(BOARD_H)]
        piece = next_piece()
        nxt   = next_piece()
        return board, piece, nxt, 0, 0, 1

    def draw_board(board, piece, nxt, score, lc, level):
        # Board border - colored based on level
        border_color = [C_BORDER, FG["bgreen"], FG["byellow"], FG["bred"]][min(level-1, 3) // 3]
        draw_box(board_row, board_col, BOARD_H + 2, BOARD_PX, "TETRIS", border_color)

        # Ghost piece — dotted, same fg color as piece
        gr = _ghost_row(board, piece)
        gp = {'kind': piece['kind'], 'rot': piece['rot'], 'row': gr, 'col': piece['col']}
        _, ghost_fg = PIECE_COLORS[piece['kind']]
        for r, c in _cells(gp):
            if 0 <= r < BOARD_H:
                put(board_row + 1 + r, board_col + 1 + c * 2, GHOST_CH, ghost_fg)

        # Locked cells — filled blocks with BG color
        for r in range(BOARD_H):
            for c in range(BOARD_W):
                k = board[r][c]
                if k:
                    bg_attr, _ = PIECE_COLORS[k]
                    put(board_row + 1 + r, board_col + 1 + c * 2, CELL, bg_attr, bold=True)

        # Active falling piece — bright BG, very visible
        bg_attr, _ = PIECE_COLORS[piece['kind']]
        for r, c in _cells(piece):
            if 0 <= r < BOARD_H:
                put(board_row + 1 + r, board_col + 1 + c * 2, CELL, bg_attr, bold=True)

        # ── Panel ──
        draw_box(board_row, panel_col, BOARD_H + 2, PANEL_W, "", C_BORDER)

        # Current piece indicator — big and obvious
        _, piece_fg = PIECE_COLORS[piece['kind']]
        put(board_row + 1, panel_col + 2, "FALLING:", C_TITLE, bold=True)
        put(board_row + 2, panel_col + 2, f" {PIECE_NAMES[piece['kind']]} ", piece_fg, bold=True)

        put(board_row + 4, panel_col + 2, "SCORE",   C_TITLE, bold=True)
        put(board_row + 5, panel_col + 2, f"{score:06d}", C_SCORE, bold=True)
        put(board_row + 7, panel_col + 2, " BEST",   C_TITLE, bold=True)
        put(board_row + 8, panel_col + 2, f"{max(score, high_score):06d}", C_SCORE)
        put(board_row + 10, panel_col + 2, "LEVEL",  C_TITLE, bold=True)
        put(board_row + 11, panel_col + 2, f"  {level:4d}", C_SCORE)
        put(board_row + 13, panel_col + 2, "LINES",  C_TITLE, bold=True)
        put(board_row + 14, panel_col + 2, f"  {lc:4d}", C_SCORE)

        # Next piece preview with color
        put(board_row + 16, panel_col + 2, " NEXT:", C_TITLE, bold=True)
        _, nxt_fg = PIECE_COLORS[nxt['kind']]
        put(board_row + 17, panel_col + 2, f" {PIECE_NAMES[nxt['kind']]} ", nxt_fg, bold=True)
        nxt_bg, _ = PIECE_COLORS[nxt['kind']]
        for r, c in TETROMINOES[nxt['kind']][0]:
            if board_row + 19 + r < sh and panel_col + 3 + c * 2 + 1 < sw:
                put(board_row + 19 + r, panel_col + 3 + c * 2, CELL, nxt_bg, bold=True)

        # Controls
        put(board_row + 16, panel_col + 1, " NEXT:", C_TITLE, bold=True)
        buf_flush()

    def draw_controls(panel_col, board_row):
        put(board_row + 16, panel_col + 1, " NEXT:  ", C_TITLE, bold=True)

    def full_redraw(board, piece, nxt, score, lc, level):
        for r in range(1, BOARD_H + 1):
            put(board_row + r, board_col + 1, EMPTY * BOARD_W)
        # Clear next piece preview area
        for r in range(19, 23):
            if board_row + r < sh:
                put(board_row + r, panel_col + 1, " " * (PANEL_W - 2))
        draw_board(board, piece, nxt, score, lc, level)

    board, piece, nxt, score, lc, level = new_game()
    flush_keys()
    last_drop = time.time()
    full_redraw(board, piece, nxt, score, lc, level)

    while True:
        drop_interval = max(0.05, 0.5 - (level - 1) * 0.04)
        key = get_key()
        moved = dict(piece)

        if key in ('a', KEY_LEFT):
            moved['col'] -= 1
            if _valid(board, _cells(moved)): piece = moved
        elif key in ('d', KEY_RIGHT):
            moved['col'] += 1
            if _valid(board, _cells(moved)): piece = moved
        elif key in ('w', KEY_UP):
            moved['rot'] = (piece['rot'] + 1) % len(TETROMINOES[piece['kind']])
            if _valid(board, _cells(moved)): piece = moved
        elif key in ('s', KEY_DOWN):
            moved['row'] += 1
            if _valid(board, _cells(moved)):
                piece = moved
                last_drop = time.time()
            else:
                board, cl = _lock(board, piece)
                lc += cl; score += LINE_SCORES[cl] * level
                level = 1 + lc // 10
                piece = nxt; nxt = next_piece()
                if not _valid(board, _cells(piece)):
                    full_redraw(board, piece, nxt, score, lc, level)
                    return _game_over(board_row, board_col, BOARD_PX, BOARD_H + 2, score, high_score)
        elif key == KEY_SPACE:
            gr = _ghost_row(board, piece)
            piece['row'] = gr
            board, cl = _lock(board, piece)
            lc += cl; score += LINE_SCORES[cl] * level
            level = 1 + lc // 10
            piece = nxt; nxt = next_piece()
            last_drop = time.time()
            if not _valid(board, _cells(piece)):
                full_redraw(board, piece, nxt, score, lc, level)
                return _game_over(board_row, board_col, BOARD_PX, BOARD_H + 2, score, high_score)
            full_redraw(board, piece, nxt, score, lc, level)
            continue
        elif key == 'q':
            return score

        # Gravity
        if time.time() - last_drop >= drop_interval:
            moved = dict(piece); moved['row'] += 1
            if _valid(board, _cells(moved)):
                piece = moved
            else:
                board, cl = _lock(board, piece)
                lc += cl; score += LINE_SCORES[cl] * level
                level = 1 + lc // 10
                piece = nxt; nxt = next_piece()
                if not _valid(board, _cells(piece)):
                    full_redraw(board, piece, nxt, score, lc, level)
                    return _game_over(board_row, board_col, BOARD_PX, BOARD_H + 2, score, high_score)
                full_redraw(board, piece, nxt, score, lc, level)
                last_drop = time.time()
                continue
            last_drop = time.time()

        draw_board(board, piece, nxt, score, lc, level)
        time.sleep(0.016)

def _game_over(board_row, board_col, box_w, box_h, score, high_score):
    ow, oh = 26, 9
    or_ = board_row + (box_h - oh) // 2
    oc  = board_col + (box_w - ow) // 2
    draw_box(or_, oc, oh, ow, "GAME OVER", C_OVER)
    put(or_ + 2, oc + 2, f"  SCORE : {score:06d}",                 C_OVER,  bold=True)
    put(or_ + 3, oc + 2, f"   BEST : {max(score, high_score):06d}", C_SCORE, bold=True)
    center_in_box(or_, oc, ow, 5, "[R] Restart", C_DIM)
    center_in_box(or_, oc, ow, 6, "[Q] Quit",    C_DIM)
    buf_flush()
    flush_keys()
    while True:
        k = wait_key()
        if k == 'r': return 'restart'
        if k == 'q': return score