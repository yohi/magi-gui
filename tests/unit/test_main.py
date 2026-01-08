"""Tests for magi_gui.main CLI launcher"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestMain:
    """Tests for the main() CLI launcher function"""

    def test_main_constructs_correct_argv(self):
        """Verify that main() constructs the correct sys.argv for streamlit"""
        from magi_gui.main import main

        with patch("streamlit.web.cli.main") as mock_stcli_main:
            mock_stcli_main.return_value = 0

            # Save original argv
            original_argv = sys.argv.copy()
            sys.argv = ["magi-gui"]

            try:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Verify exit code
                assert exc_info.value.code == 0

                # Verify stcli.main was called
                mock_stcli_main.assert_called_once()

                # Verify sys.argv was modified correctly
                assert sys.argv[0] == "streamlit"
                assert sys.argv[1] == "run"
                assert "app.py" in sys.argv[2]
            finally:
                sys.argv = original_argv

    def test_main_passes_additional_args(self):
        """Verify that additional CLI arguments are passed through"""
        from magi_gui.main import main

        with patch("streamlit.web.cli.main") as mock_stcli_main:
            mock_stcli_main.return_value = 0

            original_argv = sys.argv.copy()
            sys.argv = ["magi-gui", "--server.port", "8080"]

            try:
                with pytest.raises(SystemExit):
                    main()

                # Verify additional args are preserved
                assert "--server.port" in sys.argv
                assert "8080" in sys.argv
            finally:
                sys.argv = original_argv

    def test_app_path_resolves_correctly(self):
        """Verify that app.py path is resolved correctly relative to main.py"""
        from magi_gui import main as main_module

        main_path = Path(main_module.__file__)
        expected_app_path = main_path.parent / "app.py"

        assert expected_app_path.exists(), f"app.py should exist at {expected_app_path}"
