from utils.terminal import put, buf_flush, get_terminal_size, FG, BG, BOLD, RESET

ARCADE_LOGO = [
    r" _____ _____ ____  __  __ ___ _   _    _    _      ",
    r"|_   _| ____|  _ \|  \/  |_ _| \ | |  / \  | |     ",
    r"  | | |  _| | |_) | |\/| || ||  \| | / _ \ | |     ",
    r"  | | | |___|  _ <| |  | || || |\  |/ ___ \| |___  ",
    r"  |_| |_____|_| \_\_|  |_|___|_| \_/_/   \_\_____|  ",
    r"       ___    ____   ____    _    ____  _____        ",
    r"      / \  \ / / _| / ___|  / \  |  _ \| ____|      ",
    r"     / _ \ V / |   | |     / _ \ | | | |  _|        ",
    r"    / ___ \| || |__| |___ / ___ \| |_| | |___       ",
    r"   /_/   \_\_| \____|\____/_/   \_\____/|_____|      ",
]

def draw_box(row, col, height, width, title="", color=None):
    c = color or FG["cyan"]
    put(row, col, "+" + "-" * (width - 2) + "+", c)
    if title:
        t  = f"[ {title} ]"
        tc = col + max(1, (width - len(t)) // 2)
        put(row, tc, t, FG["bwhite"], bold=True)
    for r in range(1, height - 1):
        put(row + r, col,           "|", c)
        put(row + r, col + width-1, "|", c)
    put(row + height - 1, col, "+" + "-" * (width - 2) + "+", c)

def center_text(row, text, color=None, bold=False, offset_col=0):
    _, sw = get_terminal_size()
    col = max(0, (sw - len(text)) // 2) + offset_col
    put(row, col, text, color or "", bold)

def center_in_box(box_row, box_col, box_width, row_in_box, text, color=None, bold=False):
    col = box_col + max(1, (box_width - len(text)) // 2)
    put(box_row + row_in_box, col, text, color or "", bold)