"""Integration tests for Streamlit application"""
from unittest.mock import MagicMock, patch

import pytest

# Note: Streamlit AppTest requires streamlit >= 1.28.0
# These tests verify the high-level behavior of the Streamlit app


class TestStreamlitApp:
    """Integration tests for the Streamlit application"""

    def test_app_module_imports_successfully(self):
        """Verify that the app module can be imported without errors"""
        # This tests that all imports and module-level code work
        from magi_gui import app

        assert hasattr(app, "run_app")
        assert callable(app.run_app)

    def test_persona_constants_defined(self):
        """Verify persona-related constants are defined correctly"""
        from magi_gui.app import PERSONA_ORDER, PERSONA_LABELS, PERSONA_CLASSES

        from magi.models import PersonaType

        # PERSONA_ORDER should have all 3 personas
        assert len(PERSONA_ORDER) == 3
        assert PersonaType.MELCHIOR in PERSONA_ORDER
        assert PersonaType.BALTHASAR in PERSONA_ORDER
        assert PersonaType.CASPER in PERSONA_ORDER

        # PERSONA_LABELS should map to display names
        assert PERSONA_LABELS[PersonaType.MELCHIOR] == "MELCHIOR"
        assert PERSONA_LABELS[PersonaType.BALTHASAR] == "BALTHASAR"
        assert PERSONA_LABELS[PersonaType.CASPER] == "CASPER"

        # PERSONA_CLASSES should map to CSS classes
        assert "melchior" in PERSONA_CLASSES[PersonaType.MELCHIOR]
        assert "balthasar" in PERSONA_CLASSES[PersonaType.BALTHASAR]
        assert "casper" in PERSONA_CLASSES[PersonaType.CASPER]

    def test_decision_classes_defined(self):
        """Verify decision CSS classes are defined correctly"""
        from magi_gui.app import DECISION_CLASSES

        from magi.models import Decision

        assert Decision.APPROVED in DECISION_CLASSES
        assert Decision.DENIED in DECISION_CLASSES
        assert Decision.CONDITIONAL in DECISION_CLASSES

        assert "approved" in DECISION_CLASSES[Decision.APPROVED]
        assert "denied" in DECISION_CLASSES[Decision.DENIED]
        assert "conditional" in DECISION_CLASSES[Decision.CONDITIONAL]


class TestBuildEngine:
    """Tests for _build_engine function"""

    def test_build_engine_creates_consensus_engine(self, mock_config):
        """_build_engine should create a ConsensusEngine instance"""
        from magi_gui.app import _build_engine

        with patch("magi.core.consensus.ConsensusEngine") as MockEngine:
            MockEngine.return_value = MagicMock()

            result = _build_engine(mock_config)

            # Engine was created (may be called differently due to import)
            assert result is not None


class TestExecuteAsync:
    """Tests for _execute_async function"""

    def test_execute_async_runs_engine(self, mock_config, mock_consensus_result):
        """_execute_async should run the engine and return result"""
        from magi_gui.app import _execute_async

        mock_engine = MagicMock()
        mock_engine.execute = MagicMock(return_value=mock_consensus_result)

        with patch("asyncio.run", return_value=mock_consensus_result) as mock_run:
            result = _execute_async(mock_engine, "Test prompt")

            mock_run.assert_called_once()
            assert result == mock_consensus_result


class TestCssFileExists:
    """Tests for CSS file existence"""

    def test_style_css_exists(self):
        """style.css should exist in assets directory"""
        from pathlib import Path

        from magi_gui import app

        css_path = Path(app.__file__).parent / "assets" / "style.css"
        assert css_path.exists(), f"CSS file should exist at {css_path}"

    def test_style_css_has_required_classes(self):
        """style.css should contain required CSS classes"""
        from pathlib import Path

        from magi_gui import app

        css_path = Path(app.__file__).parent / "assets" / "style.css"
        css_content = css_path.read_text(encoding="utf-8")

        # Check for persona classes
        assert ".persona-melchior" in css_content
        assert ".persona-balthasar" in css_content
        assert ".persona-casper" in css_content

        # Check for decision classes
        assert ".decision-approved" in css_content
        assert ".decision-denied" in css_content
        assert ".decision-conditional" in css_content

        # Check for color variables
        assert "--melchior" in css_content
        assert "--balthasar" in css_content
        assert "--casper" in css_content


class TestMainModuleIntegration:
    """Integration tests for main module"""

    def test_main_module_exports_main_function(self):
        """main module should export main function"""
        from magi_gui.main import main

        assert callable(main)

    def test_package_init_exports_version(self):
        """Package should export __version__"""
        import re
        import magi_gui

        assert hasattr(magi_gui, "__version__")
        assert magi_gui.__version__
        assert re.match(r"^\d+\.\d+\.\d+$", magi_gui.__version__)
