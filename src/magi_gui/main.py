"""MAGI GUI CLI launcher"""
import sys
from pathlib import Path


def main() -> None:
    """Launch Streamlit application"""
    from streamlit.web import cli as stcli
    
    app_path = Path(__file__).parent / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)] + sys.argv[1:]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
