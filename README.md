# 🕹️ Terminal Arcade

A collection of retro-style classic games playable directly in your terminal — built with pure Python, no extra packages required.

```
 _____ _____ ____  __  __ ___ _   _    _    _
|_   _| ____|  _ \|  \/  |_ _| \ | |  / \  | |
  | | |  _| | |_) | |\/| || ||  \| | / _ \ | |
  | | | |___|  _ <| |  | || || |\  |/ ___ \| |___
  |_| |_____|_| \_\_|  |_|___|_| \_/_/   \_\_____|
```

---

## 🎮 Games

| Game   | Description           | Features |
|--------|-----------------------|----------|
| 🐍 Snake  | Eat, grow, survive    | Directional head, progressive speed, length tracker |
| 🟦 Tetris | Stack the blocks      | Ghost piece, 7-bag randomizer, hard drop, piece preview |

---

## 💻 Requirements

- **Python 3.7+**
- Terminal at least **72 × 26** characters (larger is better)
- **No pip installs needed** — uses only the Python standard library
- Works on **Windows PowerShell**, **Windows Terminal**, **macOS**, and **Linux**

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YourUsername/terminal-arcade.git
cd terminal-arcade
```

### 2. Run the arcade
```bash
python main.py
```

On Windows PowerShell:
```powershell
python main.py
```

---

## 📁 Project Structure

```
terminal-arcade/
├── main.py              # Main menu & game launcher
├── games/
│   ├── __init__.py
│   ├── snake.py         # Snake game
│   └── tetris.py        # Tetris game
└── utils/
    ├── __init__.py
    ├── terminal.py      # ANSI rendering + Windows keyboard input
    └── display.py       # Shared UI helpers (boxes, centering, logo)
```

---

## 🎯 Controls

### Main Menu
| Key | Action |
|-----|--------|
| `W` / `S` or `↑` / `↓` | Navigate |
| `Enter` / `Space` | Select game |
| `Q` | Quit |

### 🐍 Snake
| Key | Action |
|-----|--------|
| `W` `A` `S` `D` or Arrow Keys | Move |
| `Q` | Quit to menu |
| `R` *(on game over)* | Restart |

### 🟦 Tetris
| Key | Action |
|-----|--------|
| `A` / `D` or `←` / `→` | Move left / right |
| `W` or `↑` | Rotate piece |
| `S` or `↓` | Soft drop |
| `Space` | Hard drop |
| `Q` | Quit to menu |
| `R` *(on game over)* | Restart |

---

## ✨ Features

- 🏆 **Persistent high scores** — saved automatically to `.high_scores.json`
- 👻 **Ghost piece** in Tetris shows where your piece will land
- ⚡ **Progressive difficulty** — speed increases as your score grows
- 🎨 **Vibrant color scheme** — each Tetris piece has a unique bright color, Snake has a directional head
- 📺 **Pure ASCII art** — retro terminal aesthetic throughout
- 🪟 **Windows native** — no `curses` dependency, works out of the box in PowerShell

---

## 🛠️ How It Works

The game engine (`utils/terminal.py`) is a custom-built renderer that:
- Uses **ANSI escape codes** for colors and cursor movement
- Enables **Virtual Terminal Processing** on Windows 10+ for full color support
- Reads keyboard input via `msvcrt` on Windows and `tty`/`termios` on Unix
- Runs input on a **background thread** so gameplay stays smooth

---

## 📜 License

MIT — play freely, fork freely.

---

*Built with Python 🐍 | No dependencies | Cross-platform*
