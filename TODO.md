# Project Requirements

These are the project requirements in a checkbox format from the Canvas turn-in spot.

# Program Requirements

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

## Future Out-of-Scope Enhancements

- Backend HTTP mode parity with demo mode
  - Implement flags and alive/win tracking in Python `Board`
  - Add `/api/flag` logic and persist state between requests
  - Optional: difficulty presets (Beginner/Intermediate/Expert)
- Game features
  - Persisted timer in backend; include elapsed time in API
  - Leaderboard (fastest time per difficulty) with a simple DB
  - Sound effects and subtle animations for reveals/flags
  - Keyboard accessibility and screen-reader improvements
  - Mobile layout polish; larger tap targets
- Quality & DX
  - Unit tests for engine (JS demo and Python back end)
  - E2E tests (Playwright) for core flows
  - CI workflow: lint, test, build
  - Deploy frontend (Netlify/Vercel) and backend (Railway/Fly.io)
- Nice-to-haves
  - Theming presets; color-blind friendly palette
  - PWA installability and offline demo mode

# Documentation Requirements

## System Documentation

### Person-Hours Estimate

- [x] Detail methodology for estimated hours

### Actual Person-Hours

- [x] Day-by-day accounting for each member's hours (excluding lectures)
- [x] Submit Excel spreadsheet PDF of hours

### System Architecture Overview

- [ ] High-level description of components
- [ ] High-level diagrams of components
- [x] High-level diagram of dataflow
- [ ] High-level diagrams of key data structures 

## Code Documentation and Comments

### Prologue Comments

- [x] Include for each file
  - [x] Function, class, module name
  - [x] Brief description
  - [x] Inputs and outputs
  - [x] External sources with attribution
  - [x] Author(s) full name(s) and creation date

### In-Code Comments

- [x] Comment major code blocks and/or individual lines to explain functionality
- [x] Indicate whether code is original, sourced, or combined
- [x] Ensure clarity for GTA and Project 2 team comprehension

# Source Attribution

- [x] Clearly identify external code sources and rephrase comments distinctly