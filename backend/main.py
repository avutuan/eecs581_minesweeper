"""
Name: main.py
Description: Entry point for the backend logic.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Riley Meyerkorth (this is what version control is for lol)
Creation Date: 10 September 2025 (this is what version control is for lol)
"""

# Support both `python -m backend.main` and `python backend/main.py`
if __name__ == "__main__" and (__package__ is None or __package__ == ""):
    # Running as a script: add project root to sys.path and use absolute import
    import os
    import sys
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from backend.controller import Controller  # type: ignore
else:
    # Running as a module: relative import works
    from .controller import Controller

if __name__ == "__main__":
    c = Controller()
    c.run()