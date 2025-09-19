# Project Requirements

These are the project requirements in a checkbox format from the Canvas turn-in spot.

## Game Setup

### Board Configuration

- [x] Size: 10x10 grid
- [x] Columns labeled A–J; rows numbered 1–10

## Mine Configuration

- [x] Number of mines: User-specified, 10 to 20
- [x] Randomly placed at game start
- [x] First clicked cell (and optionally adjacent cells) guaranteed mine-free
- [x] Initial State: All cells start covered, with no flags

## Gameplay

- [x] Players uncover a cell by selecting it (e.g., clicking)
- [x] Uncovering a mine ends the game (loss)
- [x] Uncovering a mine-free cell reveals a number (0–8) indicating adjacent mines
- [x] Cells with zero adjacent mines trigger recursive uncovering of adjacent cells
- [x] Players can toggle flags on covered cells to mark suspected mines

## Mine Flagging

- [x] Players place/remove flags on covered cells to indicate potential mines
- [x] Flagged cells cannot be uncovered until unflagged
- [x] Display remaining flag count (total mines minus placed flags)

## Player Interface

- [x] Display a 10x10 grid showing cell states: covered, flagged, or uncovered (number or empty for zero adjacent mines)
- [x] Show remaining mine count (total mines minus flags)
- [x] Provide a status indicator (e.g., “Playing,” “Game Over: Loss,” “Victory”)

## Game Conclusion

- [x] Loss: Triggered by uncovering a mine, revealing all mines
- [x] Win: Achieved by uncovering all non-mine cells without detonating any mines
