"""Tests for magi_gui.app pure functions"""
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from magi.errors import MagiError, MagiException
from magi.models import PersonaType, ThinkingOutput, Vote, VoteOutput


class TestSetGeminiEnv:
    """Tests for _set_gemini_env function"""

    def test_sets_all_environment_variables(self, clean_env):
        """Verify all required environment variables are set"""
        from magi_gui.app import _set_gemini_env

        _set_gemini_env(
            api_key="test-key",
            model="gemini-1.5-flash",
            endpoint="https://example.com",
        )

        assert os.environ["MAGI_DEFAULT_PROVIDER"] == "gemini"
        assert os.environ["MAGI_API_KEY"] == "test-key"
        assert os.environ["MAGI_MODEL"] == "gemini-1.5-flash"
        assert os.environ["MAGI_GEMINI_API_KEY"] == "test-key"
        assert os.environ["MAGI_GEMINI_MODEL"] == "gemini-1.5-flash"
        assert os.environ["MAGI_GEMINI_ENDPOINT"] == "https://example.com"

    def test_overwrites_existing_values(self, clean_env, monkeypatch):
        """Verify existing environment variables are overwritten"""
        from magi_gui.app import _set_gemini_env

        monkeypatch.setenv("MAGI_API_KEY", "old-key")

        _set_gemini_env(
            api_key="new-key",
            model="gemini-1.5-pro",
            endpoint="https://new.example.com",
        )

        assert os.environ["MAGI_API_KEY"] == "new-key"


class TestNormalizeThinking:
    """Tests for _normalize_thinking function"""

    def test_normalizes_persona_type_keys(self, mock_thinking_results):
        """PersonaType keys should pass through unchanged"""
        from magi_gui.app import _normalize_thinking

        result = _normalize_thinking(mock_thinking_results)

        assert PersonaType.MELCHIOR in result
        assert PersonaType.BALTHASAR in result
        assert PersonaType.CASPER in result

    def test_normalizes_string_keys(self):
        """String keys should be converted to PersonaType"""
        from magi_gui.app import _normalize_thinking

        now = datetime.now()
        input_data = {
            "melchior": ThinkingOutput(
                persona_type=PersonaType.MELCHIOR,
                content="Test content",
                timestamp=now,
            ),
        }

        result = _normalize_thinking(input_data)

        assert PersonaType.MELCHIOR in result
        assert result[PersonaType.MELCHIOR].content == "Test content"

    def test_handles_empty_dict(self):
        """Empty dict should return empty dict"""
        from magi_gui.app import _normalize_thinking

        result = _normalize_thinking({})

        assert result == {}


class TestNormalizeVotes:
    """Tests for _normalize_votes function"""

    def test_normalizes_persona_type_keys(self, mock_voting_results):
        """PersonaType keys should pass through unchanged"""
        from magi_gui.app import _normalize_votes

        result = _normalize_votes(mock_voting_results)

        assert PersonaType.MELCHIOR in result
        assert PersonaType.BALTHASAR in result
        assert PersonaType.CASPER in result

    def test_normalizes_string_keys(self):
        """String keys should be converted to PersonaType"""
        from magi_gui.app import _normalize_votes

        input_data = {
            "casper": VoteOutput(
                persona_type=PersonaType.CASPER,
                vote=Vote.DENY,
                reason="Test reason",
                conditions=None,
            ),
        }

        result = _normalize_votes(input_data)

        assert PersonaType.CASPER in result
        assert result[PersonaType.CASPER].vote == Vote.DENY


class TestRenderErrorMessage:
    """Tests for _render_error_message function"""

    def test_formats_magi_exception_with_error_object(self):
        """MagiException with error object should be formatted correctly"""
        from magi_gui.app import _render_error_message

        error = MagiError(code="CONFIG_001", message="Invalid configuration")
        exc = MagiException(error)

        result = _render_error_message(exc)

        assert result == "CONFIG_001: Invalid configuration"

    def test_formats_magi_exception_fallback(self):
        """MagiException without proper attributes should use fallback"""
        from magi_gui.app import _render_error_message

        error = MagiError(code="TEST_001", message="Simple error message")
        exc = MagiException(error)

        result = _render_error_message(exc)

        assert "Simple error message" in result


class TestLoadCss:
    """Tests for _load_css function"""

    def test_loads_existing_css_file(self):
        """CSS file should be loaded when it exists"""
        from magi_gui.app import _load_css

        with patch("streamlit.markdown") as mock_markdown:
            _load_css()

            # Verify markdown was called with CSS content
            mock_markdown.assert_called_once()
            call_args = mock_markdown.call_args
            assert "<style>" in call_args[0][0]
            assert call_args[1]["unsafe_allow_html"] is True


class TestInitSessionState:
    """Tests for _init_session_state function"""

    def test_initializes_default_values(self, clean_env):
        """Session state should be initialized with default values"""
        from magi_gui.app import _init_session_state

        # Use a class that supports 'in' operator and attribute assignment
        class MockSessionState(dict):
            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError:
                    raise AttributeError(key)

            def __setattr__(self, key, value):
                self[key] = value

        mock_session_state = MockSessionState()

        with patch("streamlit.session_state", mock_session_state):
            _init_session_state()

            assert "api_key" in mock_session_state
            assert "model" in mock_session_state
            assert mock_session_state["model"] == "gemini-1.5-pro"
            assert "debate_rounds" in mock_session_state
            assert mock_session_state["debate_rounds"] == 3

    def test_uses_environment_variable_for_api_key(self, monkeypatch):
        """API key should be read from environment variable if set"""
        from magi_gui.app import _init_session_state

        monkeypatch.setenv("MAGI_GEMINI_API_KEY", "env-api-key")

        class MockSessionState(dict):
            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError:
                    raise AttributeError(key)

            def __setattr__(self, key, value):
                self[key] = value

        mock_session_state = MockSessionState()

        with patch("streamlit.session_state", mock_session_state):
            _init_session_state()

            assert mock_session_state["api_key"] == "env-api-key"

    def test_does_not_overwrite_existing_values(self):
        """Existing session state values should not be overwritten"""
        from magi_gui.app import _init_session_state

        class MockSessionState(dict):
            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError:
                    raise AttributeError(key)

            def __setattr__(self, key, value):
                self[key] = value

        mock_session_state = MockSessionState(
            {"api_key": "existing-key", "model": "gemini-1.5-flash"}
        )

        with patch("streamlit.session_state", mock_session_state):
            _init_session_state()

            assert mock_session_state["api_key"] == "existing-key"
            assert mock_session_state["model"] == "gemini-1.5-flash"
