"""
Name: server.py
Description: The FastAPI server for the Minesweeper backend.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Nicholas Holmes
Creation Date: 18 September 2025
"""
import random

from typing import Optional

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import (
    BoardFrontendModel,
    BoardPos,
    NewGameParams,
    BoardSize,
    GameMode,
    PlayerType,
)

from .constants import (
    API_HOST,
    API_PORT,
    APIRoutes,
)

from .board import Board


class Server:
    """
    Description: Encapsulates the Minesweeper game state and exposes FastAPI
    routes. This class avoids module-level globals by containing the FastAPI
    application instance, the active Board, and related runtime flags. Routes
    are registered on construction and operate against the instance's board
    state.
    Inputs: None
    Outputs: None
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    External Sources: FastAPI, pydantic
    """

    def __init__(self):
        """
        Description: Initialize the FastAPI app, CORS middleware, and routes.
        Inputs: None
        Outputs: None
        Author(s): Nicholas Holmes
        Creation Date: 18 September 2025
        External Sources: FastAPI
        """

        self.app = FastAPI()

        # Add CORS middleware to allow frontend to connect
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In prod, specify the frontend URL
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.board: Optional[Board] = None
        self.initialized: bool = False
        self.alive: bool = True
        self.game_mode: GameMode = GameMode.SOLO
        self.ai_difficulty: str = "medium"

        router = APIRouter()

        @router.post(APIRoutes.API_ROUTE_NEW_GAME)
        def new_game(params: NewGameParams):
            """
            Description: Start a new game.
            Inputs: params (NewGameParams) - validated new game parameters
            Outputs: BoardFrontendModel containing ok/error and optional state
            Author(s): Nicholas Holmes, Changwen Gong
            Creation Date: 18 September 2025
            External Sources: pydantic ValidationError
            """
            try:
                self.game_mode = params.game_mode
                self.ai_difficulty = params.ai_difficulty
                self.board = Board(params.mines, self.game_mode)
                self.board.size = BoardSize(params.rows, params.cols)
                self.board.board = [[0 for _ in range(params.cols)] for _ in range(params.rows)]
                self.board.revealed = [[False for _ in range(params.cols)] for _ in range(params.rows)]
                self.board.flags = [[False for _ in range(params.cols)] for _ in range(params.rows)]
                self.board.flag_count = 0
                self.board.isAlive = True
                self.initialized = False
                self.alive = True
                return BoardFrontendModel(ok=True, state=self.board.to_dict())
            except ValidationError as e:
                return BoardFrontendModel(ok=False, error=str(e))
            except Exception as e:
                return BoardFrontendModel(ok=False, error=f"Failed to create new game: {str(e)}")

        @router.get(APIRoutes.API_ROUTE_STATE)
        def state():
            """
            Description: Retrieve the current game state.
            Inputs: None
            Outputs: BoardFrontendModel with current state or error message
            Author(s): Nicholas Holmes
            Creation Date: 18 September 2025
            External Sources: N/A
            """
            # If no board exists, return an error
            if self.board is None:
                return BoardFrontendModel(ok=False, error="No game in progress")
            # Otherwise, return the current state
            state_model = self.board.to_dict(reveal_all=(not self.alive))
            return BoardFrontendModel(
                ok=True,
                state=state_model,
                alive=self.alive,
                win=self.board.check_win(),
            )

        @router.post(APIRoutes.API_ROUTE_CLICK)
        def click(c: BoardPos):
            """
            Description: Process a click at the provided board position.
            Outputs: BoardFrontendModel with updated state and alive/win status
            Author(s): Nicholas Holmes, Kobe Jordan
            Creation Date: 18 September 2025
            External Sources: Board implementation
            """
            if self.board is None:
                return BoardFrontendModel(ok=False, error="No board available to click")
            
            # Check co-op mode turn restrictions
            if self.game_mode == GameMode.COOP:
                if self.board.current_player != PlayerType.HUMAN:
                    return BoardFrontendModel(ok=False, error="Not your turn")
                if not self.board.human_alive:
                    return BoardFrontendModel(ok=False, error="Human player is out")
            
            if not self.alive:
                return BoardFrontendModel(
                    ok=True,
                    state=self.board.to_dict(reveal_all=True),
                    alive=self.alive,
                    win=False,
                )

            # First click: place mines and compute counts
            if not self.initialized:
                self.board.place_mines(BoardPos(x=c.x, y=c.y))
                self.board.update_mine_counts()
                self.initialized = True

            # Handle the move based on game mode
            if self.game_mode == GameMode.COOP:
                print(f"[DEBUG] Human move in co-op mode - before: current_player={self.board.current_player}")
                success = self.board.handle_player_move(BoardPos(x=c.x, y=c.y), PlayerType.HUMAN)
                self.alive = success
                win = self.board.check_coop_win()
                print(f"[DEBUG] Human move in co-op mode - after: current_player={self.board.current_player}, success={success}")
            else:
                self.alive = self.board.reveal_cell(BoardPos(x=c.x, y=c.y))
                win = self.board.check_win()

            return BoardFrontendModel(
                ok=True,
                alive=self.alive,
                win=win,
                state=self.board.to_dict(reveal_all=(not self.alive)),
            )

        @router.post(APIRoutes.API_ROUTE_FLAG)
        def toggle_flag(c: BoardPos):
            """
            Description: Toggle a flag at the provided board position.
            Inputs: c (BoardPos) - position to toggle flag
            Outputs: BoardFrontendModel with updated state
            Author(s): Nicholas Holmes, Kobe Jordan
            Creation Date: 18 September 2025
            External Sources: N/A
            """
            if self.board is None:
                return BoardFrontendModel(ok=False, error="No board available to flag")
            
            # Check co-op mode turn restrictions
            if self.game_mode == GameMode.COOP:
                if self.board.current_player != PlayerType.HUMAN:
                    return BoardFrontendModel(ok=False, error="Not your turn")
                if not self.board.human_alive:
                    return BoardFrontendModel(ok=False, error="Human player is out")
            
            if not self.alive:
                return BoardFrontendModel(
                    ok=True,
                    alive=self.alive,
                    win=False,
                    state=self.board.to_dict(reveal_all=True),
                )

            self.board.flag_cell(BoardPos(x=c.x, y=c.y))
            
            # In co-op mode, flagging should switch turns to AI
            if self.game_mode == GameMode.COOP:
                self.board.current_player = PlayerType.AI
                print(f"[DEBUG] Flag move in co-op mode - switched to AI turn")

            return BoardFrontendModel(
                ok=True,
                state=self.board.to_dict(),
                alive=self.alive,
                win=self.board.check_win(),
            )

        @router.get("/api/ai/{difficulty}")
        def ai_move(difficulty: str):
            """
            Description: Compute and apply an AI move based on the specified difficulty.
            Inputs: difficulty (str) - one of 'easy', 'medium', 'hard'
            Outputs: dict containing 'action', 'pos', and 'state' or an error
            Author(s): Raj Kaura, Kobe Jordan
            Creation Date: 1 October 2025
            External Sources: N/A
            """
            if not self.initialized:
                rows = self.board.size.rows
                cols = self.board.size.cols

                # pick a random hidden cell
                r = random.randrange(rows)
                c = random.randrange(cols)
                first_pos = BoardPos(x=r, y=c)

                # place mines around that first click and compute counts
                self.board.place_mines(first_pos)
                self.board.update_mine_counts()
                self.initialized = True

                # reveal the chosen cell (will not be a mine because place_mines avoids it)
                self.alive = self.board.reveal_cell(first_pos)

                # return the state after the initial reveal so the frontend can update
                return {
                    "action": "reveal",
                    "pos": first_pos.dict(),
                    "state": self.board.to_dict(reveal_all=(not self.alive)),
                }

            if difficulty == "easy":
                action, pos = self.board.ai_move_easy()
            elif difficulty == "medium":
                action, pos = self.board.ai_move_medium()
            elif difficulty == "hard":
                action, pos = self.board.ai_move_hard()
            else:
                return {"error": "Invalid difficulty"}

            if pos is None:
                return {"action": "none", "pos": None}

            # Apply the move
            if action == "reveal":
                self.alive = self.board.reveal_cell(pos)
            elif action == "flag":
                self.board.flag_cell(pos)

            return {
                "action": action,
                "pos": pos.dict() if pos else None,
                "state": self.board.to_dict(reveal_all=(not self.alive)),
            }

        @router.post("/api/ai-turn")
        def ai_turn():
            """
            Description: Compute and apply an AI move based on the specified difficulty.
            Inputs: None (uses server's stored board & difficulty)
            Outputs: BoardFrontendModel with updated state and alive/win flags
            Author(s): Raj Kaura, Kobe Jordan
            Creation Date: 1 October 2025
            External Sources: N/A
            """
            print(f"[DEBUG] AI turn requested - game_mode: {self.game_mode}, current_player: {self.board.current_player if self.board else None}")
            print(f"[DEBUG] AI turn conditions - board exists: {self.board is not None}, game_mode: {self.game_mode}, current_player: {self.board.current_player if self.board else None}, ai_alive: {self.board.ai_alive if self.board else None}")
            
            if self.board is None:
                print("[DEBUG] AI turn failed: No board")
                return BoardFrontendModel(ok=False, error="No game in progress")
            if self.game_mode != GameMode.COOP:
                print("[DEBUG] AI turn failed: Not in co-op mode")
                return BoardFrontendModel(ok=False, error="Not in co-op mode")
            if self.board.current_player != PlayerType.AI:
                print(f"[DEBUG] AI turn failed: Not AI's turn (current: {self.board.current_player})")
                return BoardFrontendModel(ok=False, error="Not AI's turn")
            if not self.board.ai_alive:
                print("[DEBUG] AI turn failed: AI not alive")
                return BoardFrontendModel(ok=False, error="AI player is out")
            
            # Make AI move based on difficulty
            if self.ai_difficulty == "easy":
                action, pos = self.board.ai_move_easy()
            elif self.ai_difficulty == "medium":
                action, pos = self.board.ai_move_medium()
            elif self.ai_difficulty == "hard":
                action, pos = self.board.ai_move_hard()
            else:
                return BoardFrontendModel(ok=False, error="Invalid AI difficulty")
            
            print(f"[DEBUG] AI move: action={action}, pos={pos}")
            
            if pos is None:
                return BoardFrontendModel(ok=False, error="AI has no moves")
            
            # Handle the AI move
            if action == "reveal":
                success = self.board.handle_player_move(pos, PlayerType.AI)
                self.alive = success
                print(f"[DEBUG] AI reveal move success: {success}")
            elif action == "flag":
                self.board.flag_cell(pos)
                # Switch turns after flagging
                self.board.current_player = PlayerType.HUMAN
                print(f"[DEBUG] AI flag move, switched to human turn")
            
            win = self.board.check_coop_win()
            
            print(f"[DEBUG] AI turn complete - current_player: {self.board.current_player}, alive: {self.alive}, win: {win}")
            
            return BoardFrontendModel(
                ok=True,
                alive=self.alive,
                win=win,
                state=self.board.to_dict(reveal_all=(not self.alive)),
            )

        # Register routes *after* defining them all
        self.app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    server = Server()
    uvicorn.run(server.app, host=API_HOST, port=API_PORT)