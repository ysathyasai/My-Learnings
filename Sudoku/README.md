# Sudoku (in `My-Learnings/Sudoku`)

> **⚡️ This project is COMPLETELY VIBE CODED.**  
> You'll find it in the repo [`ysathyasai/My-Learnings`](https://github.com/ysathyasai/My-Learnings), under the `Sudoku` folder.

A feature-rich Sudoku game for the terminal, written in Python. Includes colorful board display, achievements, high score tracking, hints, note-taking, save/load capability, undo/redo, and more.

## Features

- **Colorful Board** with highlighting and conflict checking (uses [colorama](https://pypi.org/project/colorama/))
- **Achievements**: Unlockable achievements for skillful or persistent play
- **High Scores**: Top scores are saved with difficulty, time, and mistakes tracked
- **Hints System**: Up to 3 hints per game
- **Notes**: Add pencil marks to cells
- **Save/Load**: Persist game state between runs
- **Undo/Redo**: Step backward/forward through your moves
- **Difficulty Levels**: Easy, Medium, Hard
- **Pause**: Pause and resume your game

## Requirements

- Python 3.7+
- See [`requirements.txt`](requirements.txt) for details

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ysathyasai/My-Learnings.git
   cd My-Learnings/Sudoku
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```bash
   python sudoku.py
   ```

## Controls

- **W/A/S/D**: Move selection (up/left/down/right)
- **1-9**: Set number in the selected cell
- **n**: Toggle note mode (then use 1-9 to add/remove notes)
- **h**: Use a hint
- **u**: Undo last move (not yet implemented)
- **r**: Redo move (not yet implemented)
- **s**: Save game
- **l**: Load game
- **p**: Pause/resume
- **tab**: Toggle auto-check for mistakes
- **q**: Quit (option to save before quitting)

## Files

- `sudoku.py` — Main game script (should be located in `My-Learnings/Sudoku/`)
- `high_scores.json` — High scores are saved here
- `achievements.json` — Achievements progress
- `sudoku_save.pkl` — Saved game state (binary)

## Tips

- Earn achievements by playing skillfully (no mistakes, speed, etc.)
- Try to get a high score by solving harder puzzles quickly with few mistakes!

## License

MIT License
