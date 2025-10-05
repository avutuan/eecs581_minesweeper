# EECS 581 Project 1: Minesweeper

This is the first project for EECS 581 - Software Engineering 2 at the University of Kansas (KU).

## Group & Team Structure

- **Project Coordinator:** Riley Meyerkorth
- **Backend Developer:** Aiden Burke
- **Backend Developer:** Brett Suhr
- **Frontend Developer:** Nick Holmes
- **Quality Assurance & Testing Lead:** Andrew Reyes
- **Documentation & Communication Lead:** Ty Farrington

## Features

- **Sound Effects**: The game includes audio feedback for key events:
  - 🔊 **Win Sound**: An uplifting ascending melody plays when you successfully complete the game
  - 💥 **Bomb Sound**: A dramatic explosion sound when you click on a mine
  - 😢 **Lose Sound**: A descending melody when the game is lost
  - Sound can be toggled on/off using the speaker button in the header

## Root Structure

- `.gitignore` - ignores Node, Python, editor artifacts, etc.
- `.vscode` - Visual Studio Code specific environment setup things. Primarily for convenience.
- `backend` - The directory that stores the backend ([docs](backend/README.md))
- `frontend` - The directory that stores the frontend ([docs](frontend/README.md))
- `REQUIREMENTS.txt` - Python dependencies (FastAPI backend optional)
- `README.md` - this file
- `TODO.md` - a basic todo list for us to keep track of things to do
- `test_minesweeper.py` - file for running tests

## Setup/Running/Building

The backend and frontend must both be running. Setup instructions for both can be found in their respective directories.

## Testing

To run test cases, run the following command in the root directory:

```bash
python test_minesweeper.py
```
