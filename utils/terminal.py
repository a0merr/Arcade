"""
Cross-platform terminal rendering engine.
Uses Windows Console API on Windows, ANSI escape codes on Linux/macOS.
No curses dependency required.
"""
import os
import sys
import threading
import time

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import msvcrt
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    ENABLE_PROCESSED_OUTPUT             = 0x0001
    ENABLE_VIRTUAL_TERMINAL_PROCESSING  = 0x0004
    handle = kernel32.GetStdHandle(-11)
    mode   = wintypes.DWORD()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    kernel32.SetConsoleMode(handle, mode.value |
                            ENABLE_PROCESSED_OUTPUT |
                            ENABLE_VIRTUAL_TERMINAL_PROCESSING)
else:
    import tty, termios, select

ESC = "\033"
def _esc(code): return f"{ESC}[{code}"

def move_cursor(row, col): return _esc(f"{row+1};{col+1}H")
def hide_cursor():         return _esc("?25l")
def show_cursor():         return _esc("?25h")
def clear_screen():        return _esc("2J") + _esc("H")

RESET = _esc("0m")
BOLD  = _esc("1m")

FG = {
    "black":   _esc("30m"),
    "red":     _esc("31m"),
    "green":   _esc("32m"),
    "yellow":  _esc("33m"),
    "blue":    _esc("34m"),
    "magenta": _esc("35m"),
    "cyan":    _esc("36m"),
    "white":   _esc("37m"),
    "bblack":  _esc("90m"),
    "bred":    _esc("91m"),
    "bgreen":  _esc("92m"),
    "byellow": _esc("93m"),
    "bblue":   _esc("94m"),
    "bmagenta":_esc("95m"),
    "bcyan":   _esc("96m"),
    "bwhite":  _esc("97m"),
}

BG = {
    "black":   _esc("40m"),
    "red":     _esc("41m"),
    "green":   _esc("42m"),
    "yellow":  _esc("43m"),
    "blue":    _esc("44m"),
    "magenta": _esc("45m"),
    "cyan":    _esc("46m"),
    "white":   _esc("47m"),
    "bred":    _esc("101m"),
    "bgreen":  _esc("102m"),
    "byellow": _esc("103m"),
    "bblue":   _esc("104m"),
    "bmagenta":_esc("105m"),
    "bcyan":   _esc("106m"),
    "bwhite":  _esc("107m"),
}

# Tetris piece colors — bright BG + black text for max visibility
PIECE_COLORS = {
    'I': (BG["bcyan"]   + FG["black"], FG["bcyan"]),    # Cyan
    'O': (BG["byellow"] + FG["black"], FG["byellow"]),  # Yellow
    'T': (BG["bmagenta"]+ FG["black"], FG["bmagenta"]), # Magenta
    'S': (BG["bgreen"]  + FG["black"], FG["bgreen"]),   # Green
    'Z': (BG["bred"]    + FG["black"], FG["bred"]),     # Red
    'J': (BG["bblue"]   + FG["black"], FG["bblue"]),   # Blue
    'L': (BG["byellow"] + FG["black"], FG["byellow"]),  # Orange-ish
}

_buf = []
def buf_write(s): _buf.append(s)
def buf_flush():
    sys.stdout.write("".join(_buf))
    sys.stdout.flush()
    _buf.clear()

def put(row, col, text, color="", bold=False, bg=""):
    parts = [move_cursor(row, col)]
    if bold:  parts.append(BOLD)
    if bg:    parts.append(bg)
    if color: parts.append(color)
    parts.append(text)
    parts.append(RESET)
    buf_write("".join(parts))

def init_screen():
    sys.stdout.write(hide_cursor() + clear_screen())
    sys.stdout.flush()

def deinit_screen():
    sys.stdout.write(show_cursor() + clear_screen() + move_cursor(0, 0))
    sys.stdout.flush()

def get_terminal_size():
    size = os.get_terminal_size()
    return size.lines, size.columns

# Key constants
KEY_UP    = "UP"
KEY_DOWN  = "DOWN"
KEY_LEFT  = "LEFT"
KEY_RIGHT = "RIGHT"
KEY_ENTER = "ENTER"
KEY_SPACE = "SPACE"
KEY_ESC   = "ESC"

_key_queue = []
_key_lock  = threading.Lock()
_stop_input = threading.Event()

def _read_key_windows():
    ch = msvcrt.getch()
    if ch in (b'\xe0', b'\x00'):
        ch2 = msvcrt.getch()
        mapping = {b'H': KEY_UP, b'P': KEY_DOWN, b'K': KEY_LEFT, b'M': KEY_RIGHT}
        return mapping.get(ch2, None)
    try:
        c = ch.decode('utf-8', errors='ignore')
        if c == '\r':   return KEY_ENTER
        if c == ' ':    return KEY_SPACE
        if c == '\x1b': return KEY_ESC
        return c.lower()
    except Exception:
        return None

def _read_key_unix():
    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            r, _, _ = select.select([sys.stdin], [], [], 0.05)
            if r:
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    m = {'A': KEY_UP, 'B': KEY_DOWN, 'C': KEY_RIGHT, 'D': KEY_LEFT}
                    return m.get(ch3, KEY_ESC)
            return KEY_ESC
        if ch in ('\r', '\n'): return KEY_ENTER
        if ch == ' ':          return KEY_SPACE
        return ch.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def _input_thread():
    while not _stop_input.is_set():
        try:
            if IS_WINDOWS:
                if msvcrt.kbhit():
                    k = _read_key_windows()
                    if k:
                        with _key_lock: _key_queue.append(k)
                else:
                    time.sleep(0.01)
            else:
                r, _, _ = select.select([sys.stdin], [], [], 0.01)
                if r:
                    k = _read_key_unix()
                    if k:
                        with _key_lock: _key_queue.append(k)
        except Exception:
            time.sleep(0.01)

_input_thread_obj = None

def start_input():
    global _input_thread_obj
    _stop_input.clear()
    _input_thread_obj = threading.Thread(target=_input_thread, daemon=True)
    _input_thread_obj.start()

def stop_input():
    _stop_input.set()

def get_key():
    with _key_lock:
        return _key_queue.pop(0) if _key_queue else None

def wait_key(timeout=None):
    start = time.time()
    while True:
        k = get_key()
        if k is not None: return k
        if timeout is not None and time.time() - start >= timeout: return None
        time.sleep(0.01)

def flush_keys():
    with _key_lock: _key_queue.clear()