"""Tests for magi_gui.app rendering functions"""
import html
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from magi.models import DebateOutput, DebateRound, Decision, PersonaType, ThinkingOutput, Vote, VoteOutput


class TestRenderPersonaBlock:
    """Tests for _render_persona_block function"""

    def test_escapes_html_in_content(self):
        """Content should be HTML-escaped to prevent XSS"""
        from magi_gui.app import _render_persona_block

        dangerous_content = "<script>alert('xss')</script>"

        with patch("streamlit.markdown") as mock_markdown:
            _render_persona_block("MELCHIOR", "persona-melchior", dangerous_content)

            call_args = mock_markdown.call_args[0][0]
            # Original dangerous content should NOT be present
            assert "<script>" not in call_args
            # Escaped version should be present
            assert html.escape(dangerous_content) in call_args

    def test_renders_correct_structure(self):
        """Output should have correct HTML structure"""
        from magi_gui.app import _render_persona_block

        with patch("streamlit.markdown") as mock_markdown:
            _render_persona_block("BALTHASAR", "persona-balthasar", "Test content")

            call_args = mock_markdown.call_args[0][0]
            assert "persona-card" in call_args
            assert "persona-balthasar" in call_args
            assert "persona-title" in call_args
            assert "BALTHASAR" in call_args
            assert "persona-content" in call_args
            assert "Test content" in call_args

    def test_handles_empty_content(self):
        """Empty content should render empty string"""
        from magi_gui.app import _render_persona_block

        with patch("streamlit.markdown") as mock_markdown:
            _render_persona_block("CASPER", "persona-casper", "")

            call_args = mock_markdown.call_args[0][0]
            assert "persona-content" in call_args

    def test_handles_none_content(self):
        """None content should render empty string"""
        from magi_gui.app import _render_persona_block

        with patch("streamlit.markdown") as mock_markdown:
            _render_persona_block("MELCHIOR", "persona-melchior", None)

            call_args = mock_markdown.call_args[0][0]
            assert "<pre class='persona-content'></pre>" in call_args


class TestRenderThinking:
    """Tests for _render_thinking function"""

    def test_creates_three_columns(self, mock_thinking_results):
        """Should create exactly 3 columns for the 3 personas"""
        from magi_gui.app import _render_thinking

        mock_cols = [MagicMock(), MagicMock(), MagicMock()]

        with patch("streamlit.columns", return_value=mock_cols) as mock_columns:
            with patch("streamlit.markdown"):
                _render_thinking(mock_thinking_results)

                mock_columns.assert_called_once_with(3)

    def test_renders_all_personas(self, mock_thinking_results):
        """All three personas should be rendered"""
        from magi_gui.app import _render_thinking

        mock_cols = [MagicMock(), MagicMock(), MagicMock()]

        with patch("streamlit.columns", return_value=mock_cols):
            with patch("streamlit.markdown") as mock_markdown:
                _render_thinking(mock_thinking_results)

                # Should have 3 calls (one per persona)
                assert mock_markdown.call_count == 3

    def test_handles_missing_persona_output(self):
        """Missing persona output should show 'No output produced.'"""
        from magi_gui.app import _render_thinking

        now = datetime.now()
        partial_results = {
            PersonaType.MELCHIOR: ThinkingOutput(
                persona_type=PersonaType.MELCHIOR,
                content="Only MELCHIOR",
                timestamp=now,
            ),
        }

        mock_cols = [MagicMock(), MagicMock(), MagicMock()]

        with patch("streamlit.columns", return_value=mock_cols):
            with patch("streamlit.markdown") as mock_markdown:
                _render_thinking(partial_results)

                all_calls = "".join(str(c) for c in mock_markdown.call_args_list)
                assert "No output produced." in all_calls


class TestRenderDebateRound:
    """Tests for _render_debate_round function"""

    def test_renders_all_personas(self, mock_debate_round):
        """All three personas should be rendered in the debate round"""
        from magi_gui.app import _render_debate_round

        with patch("streamlit.markdown") as mock_markdown:
            _render_debate_round(mock_debate_round)

            # Should render 3 persona blocks
            assert mock_markdown.call_count == 3

    def test_formats_responses_correctly(self, mock_debate_round):
        """Responses should be formatted with 'To <persona>:' prefix"""
        from magi_gui.app import _render_debate_round

        with patch("streamlit.markdown") as mock_markdown:
            _render_debate_round(mock_debate_round)

            all_calls = "".join(str(c) for c in mock_markdown.call_args_list)
            assert "To BALTHASAR:" in all_calls or "To CASPER:" in all_calls


class TestRenderVotingTable:
    """Tests for _render_voting_table function"""

    def test_creates_table_with_all_personas(self, mock_voting_results):
        """Table should include all three personas"""
        from magi_gui.app import _render_voting_table

        with patch("streamlit.table") as mock_table:
            _render_voting_table(mock_voting_results)

            mock_table.assert_called_once()
            rows = mock_table.call_args[0][0]
            assert len(rows) == 3

            persona_names = [row["Persona"] for row in rows]
            assert "MELCHIOR" in persona_names
            assert "BALTHASAR" in persona_names
            assert "CASPER" in persona_names

    def test_formats_vote_values_uppercase(self, mock_voting_results):
        """Vote values should be uppercase"""
        from magi_gui.app import _render_voting_table

        with patch("streamlit.table") as mock_table:
            _render_voting_table(mock_voting_results)

            rows = mock_table.call_args[0][0]
            for row in rows:
                assert row["Vote"] == row["Vote"].upper()

    def test_handles_missing_vote_output(self):
        """Missing vote output should show 'N/A'"""
        from magi_gui.app import _render_voting_table

        partial_results = {
            PersonaType.MELCHIOR: VoteOutput(
                persona_type=PersonaType.MELCHIOR,
                vote=Vote.APPROVE,
                reason="Test",
                conditions=None,
            ),
        }

        with patch("streamlit.table") as mock_table:
            _render_voting_table(partial_results)

            rows = mock_table.call_args[0][0]
            na_rows = [r for r in rows if r["Vote"] == "N/A"]
            assert len(na_rows) == 2  # BALTHASAR and CASPER

    def test_formats_conditions(self, mock_voting_results):
        """Conditions should be joined with ' | '"""
        from magi_gui.app import _render_voting_table

        with patch("streamlit.table") as mock_table:
            _render_voting_table(mock_voting_results)

            rows = mock_table.call_args[0][0]
            balthasar_row = next(r for r in rows if r["Persona"] == "BALTHASAR")
            assert " | " in balthasar_row["Conditions"]


class TestRenderFinalDecision:
    """Tests for _render_final_decision function"""

    @pytest.mark.parametrize(
        "decision,expected_class",
        [
            (Decision.APPROVED, "decision-approved"),
            (Decision.DENIED, "decision-denied"),
            (Decision.CONDITIONAL, "decision-conditional"),
        ],
    )
    def test_applies_correct_css_class(self, decision, expected_class):
        """Correct CSS class should be applied based on decision"""
        from magi_gui.app import _render_final_decision

        with patch("streamlit.markdown") as mock_markdown:
            _render_final_decision(decision, [])

            call_args = mock_markdown.call_args_list[0][0][0]
            assert expected_class in call_args

    def test_displays_decision_value_uppercase(self):
        """Decision value should be displayed in uppercase"""
        from magi_gui.app import _render_final_decision

        with patch("streamlit.markdown") as mock_markdown:
            _render_final_decision(Decision.APPROVED, [])

            call_args = mock_markdown.call_args_list[0][0][0]
            assert "APPROVED" in call_args

    def test_renders_conditions_when_present(self):
        """Conditions should be rendered when provided"""
        from magi_gui.app import _render_final_decision

        conditions = ["Condition 1", "Condition 2"]

        with patch("streamlit.markdown") as mock_markdown:
            _render_final_decision(Decision.CONDITIONAL, conditions)

            # Should have multiple markdown calls: banner + conditions header + items
            assert mock_markdown.call_count >= 2

    def test_skips_conditions_when_empty(self):
        """Conditions section should not be rendered when empty"""
        from magi_gui.app import _render_final_decision

        with patch("streamlit.markdown") as mock_markdown:
            _render_final_decision(Decision.APPROVED, [])

            # Only the banner should be rendered
            assert mock_markdown.call_count == 1
