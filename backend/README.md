# Backend

## File Structure

- `__init__.py` - initializes a Python module for this folder
- `board.py` - the main board class where almost all game logic takes place
- `constants.py` - constants that attempt to replace magic values
- `models.py` - data models and classes
- `controller.py` - the controller class for the CLI version; NOT the main game/server
- `main.py` - the entry point for the CLI; NOT the main game/server
- `server.py` - the main server class and routes for the API

## Starting the Server

### 1

Ensure that you are within the root repo directory.

### 2

Ensure that the required packages are installed by running the following command:

```bash
pip install -r requirements.txt
```

### 3

Run the following:

```bash
python -m backend.server
```

The server will now be running.
