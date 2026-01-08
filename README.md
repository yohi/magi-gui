# MAGI GUI

Streamlit GUI frontend for magi-core consensus engine.

## Requirements

- Python 3.11+
- Local magi-core checkout at `../magi-core`

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install with uv (recommended)
uv pip install -e .

# Or install with pip
pip install -e .
```

## Run

```bash
# Using the CLI command
magi-gui

# Or run directly with streamlit
streamlit run src/magi_gui/app.py
```

## Configuration

The GUI provides a sidebar with the following configuration options:

- **Gemini API Key**: Your Google Gemini API key (required)
- **Model**: Select between `gemini-1.5-pro` and `gemini-1.5-flash`
- **Debate Rounds**: Number of debate rounds (1-5)

## Environment Variables

The app automatically sets the following environment variables when running:

- `MAGI_DEFAULT_PROVIDER=gemini`
- `MAGI_GEMINI_API_KEY` - Your API key
- `MAGI_GEMINI_MODEL` - Selected model
- `MAGI_GEMINI_ENDPOINT=https://generativelanguage.googleapis.com`

## Usage

1. Enter your Gemini API key in the sidebar
2. Select your preferred model
3. Adjust debate rounds as needed
4. Enter your prompt in the text area
5. Click "INITIALIZE" to run the consensus engine
6. View results: Thinking, Debate, Voting, and Final Decision

## Project Structure

```
magi-gui/
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── src/
    └── magi_gui/
        ├── __init__.py     # Package init
        ├── main.py         # CLI launcher
        ├── app.py          # Main Streamlit application
        └── assets/
            └── style.css   # Custom CSS styles
```

## Error Handling

The GUI catches `MagiException` errors and displays:
- Error code (e.g., `CONFIG_001`)
- Error message

Generic exceptions are also caught and displayed with a user-friendly message.
