## EECS 581 Project 1: Minesweeper
### Group:
- Aiden Burke
- Nick Holmes
- Riley Meyerkorth
- Andrew Reyes
- Brett Suhr
- Ty Farrington

### Roadmap:
- Set up backend functionality for storing the minesweeper board
- Determine the optimal way to algorithmically generate mines
  - Current setup is just randomly generating them after the first click to guarantee that the first spot isnt a mine
  - More accurate to the original game might be to generate mines before the first click, then if the first spot selected is a mine, moving that mine to a new random spot (or a designated spot)
  - Building on that, maybe do the same thing to the 8 adjacent squares to guarantee that the first click is a '0' (has no adjacent mines), which I think is what the game does
- Integrate that into UI and frontend through JS and Svelte
- 
