"""
Name: server.py
Description: The FastAPI server for the Minesweeper backend.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Nicholas Holmes
Creation Date: 18 September 2025
"""

from typing import Optional

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    BoardFrontendModel,
    BoardPos,
    NewGameParams,
    BoardSize,
)

from .constants import (
    API_HOST,
    API_PORT,
    APIRoutes,
)

from .board import Board


class Server:
    """
    Encapsulates game state and exposes FastAPI routes without globals.
    """

    def __init__(self):
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

        router = APIRouter()

        @router.post(APIRoutes.API_ROUTE_NEW_GAME)
        def new_game(params: NewGameParams):
            """
            Start a new game.
            """
            self.board = Board(params.mines)
            self.board.size = BoardSize(params.rows, params.cols)
            self.board.board = [[0 for _ in range(params.cols)] for _ in range(params.rows)]
            self.board.revealed = [[False for _ in range(params.cols)] for _ in range(params.rows)]
            self.board.flags = [[False for _ in range(params.cols)] for _ in range(params.rows)]
            self.board.flag_count = 0
            self.board.isAlive = True
            self.initialized = False
            self.alive = True
            return BoardFrontendModel(ok=True, state=self.board.to_dict())

        @router.get(APIRoutes.API_ROUTE_STATE)
        def state():
            """
            Return the current game state.
            """
            if self.board is None:
                return BoardFrontendModel(ok=False, error="No game in progress")
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
            Handle a user click.
            """
            if self.board is None:
                return BoardFrontendModel(ok=False, error="No board available to click")
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
            Toggle a flag at the given position.
            """
            if self.board is None:
                return BoardFrontendModel(ok=False, error="No board available to flag")
            if not self.alive:
                return BoardFrontendModel(
                    ok=True,
                    alive=self.alive,
                    win=False,
                    state=self.board.to_dict(reveal_all=True),
                )

            self.board.flag_cell(BoardPos(x=c.x, y=c.y))

            return BoardFrontendModel(
                ok=True,
                state=self.board.to_dict(),
                alive=self.alive,
                win=self.board.check_win(),
            )

        @router.get("/api/ai/{difficulty}")
        def ai_move(difficulty: str):
            """
            Perform an AI move for the given difficulty.
            """
            if self.board is None:
                return {"error": "No board"}
            if not self.alive:
                return {"error": "Game over"}

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

        # Register routes *after* defining them all
        self.app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    server = Server()
    uvicorn.run(server.app, host=API_HOST, port=API_PORT)
