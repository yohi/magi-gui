"""Shared test fixtures for magi-gui tests"""
import os
from datetime import datetime
from typing import Dict
from unittest.mock import MagicMock

import pytest

from magi.models import (
    ConsensusResult,
    DebateOutput,
    DebateRound,
    Decision,
    PersonaType,
    ThinkingOutput,
    Vote,
    VoteOutput,
)


@pytest.fixture
def mock_thinking_results() -> Dict[PersonaType, ThinkingOutput]:
    """Create mock thinking results for all personas"""
    now = datetime.now()
    return {
        PersonaType.MELCHIOR: ThinkingOutput(
            persona_type=PersonaType.MELCHIOR,
            content="MELCHIOR analysis: Scientific perspective on the matter.",
            timestamp=now,
        ),
        PersonaType.BALTHASAR: ThinkingOutput(
            persona_type=PersonaType.BALTHASAR,
            content="BALTHASAR analysis: Nurturing and protective considerations.",
            timestamp=now,
        ),
        PersonaType.CASPER: ThinkingOutput(
            persona_type=PersonaType.CASPER,
            content="CASPER analysis: Emotional and intuitive insights.",
            timestamp=now,
        ),
    }


@pytest.fixture
def mock_debate_round() -> DebateRound:
    """Create a mock debate round"""
    now = datetime.now()
    return DebateRound(
        round_number=1,
        outputs={
            PersonaType.MELCHIOR: DebateOutput(
                persona_type=PersonaType.MELCHIOR,
                round_number=1,
                responses={
                    PersonaType.BALTHASAR: "Response to BALTHASAR from MELCHIOR.",
                    PersonaType.CASPER: "Response to CASPER from MELCHIOR.",
                },
                timestamp=now,
            ),
            PersonaType.BALTHASAR: DebateOutput(
                persona_type=PersonaType.BALTHASAR,
                round_number=1,
                responses={
                    PersonaType.MELCHIOR: "Response to MELCHIOR from BALTHASAR.",
                    PersonaType.CASPER: "Response to CASPER from BALTHASAR.",
                },
                timestamp=now,
            ),
            PersonaType.CASPER: DebateOutput(
                persona_type=PersonaType.CASPER,
                round_number=1,
                responses={
                    PersonaType.MELCHIOR: "Response to MELCHIOR from CASPER.",
                    PersonaType.BALTHASAR: "Response to BALTHASAR from CASPER.",
                },
                timestamp=now,
            ),
        },
        timestamp=now,
    )


@pytest.fixture
def mock_voting_results() -> Dict[PersonaType, VoteOutput]:
    """Create mock voting results for all personas"""
    return {
        PersonaType.MELCHIOR: VoteOutput(
            persona_type=PersonaType.MELCHIOR,
            vote=Vote.APPROVE,
            reason="Scientific analysis supports approval.",
            conditions=None,
        ),
        PersonaType.BALTHASAR: VoteOutput(
            persona_type=PersonaType.BALTHASAR,
            vote=Vote.CONDITIONAL,
            reason="Approval with safety conditions.",
            conditions=["Implement safety measures", "Monitor outcomes"],
        ),
        PersonaType.CASPER: VoteOutput(
            persona_type=PersonaType.CASPER,
            vote=Vote.APPROVE,
            reason="Intuitive assessment favors approval.",
            conditions=None,
        ),
    }


@pytest.fixture
def mock_consensus_result(
    mock_thinking_results: Dict[PersonaType, ThinkingOutput],
    mock_debate_round: DebateRound,
    mock_voting_results: Dict[PersonaType, VoteOutput],
) -> ConsensusResult:
    """Create a complete mock ConsensusResult"""
    return ConsensusResult(
        thinking_results=mock_thinking_results,
        debate_results=[mock_debate_round],
        voting_results=mock_voting_results,
        final_decision=Decision.APPROVED,
        exit_code=0,
        all_conditions=["Implement safety measures", "Monitor outcomes"],
    )


@pytest.fixture
def mock_config() -> MagicMock:
    """Create a mock Config object"""
    config = MagicMock()
    config.api_key = "test-api-key"
    config.model = "gemini-1.5-flash"
    config.debate_rounds = 2
    return config


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch):
    """Clean environment variables before test"""
    env_vars = [
        "MAGI_DEFAULT_PROVIDER",
        "MAGI_API_KEY",
        "MAGI_MODEL",
        "MAGI_GEMINI_API_KEY",
        "MAGI_GEMINI_MODEL",
        "MAGI_GEMINI_ENDPOINT",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
    yield
    # Cleanup happens automatically via monkeypatch
