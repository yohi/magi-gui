"""Report generation utilities for MAGI GUI

This module provides functionality to generate Markdown reports from
ConsensusResult objects.
"""
from datetime import datetime
from typing import Dict, List, Optional

from magi.models import (
    ConsensusResult,
    DebateRound,
    Decision,
    PersonaType,
    ThinkingOutput,
    VoteOutput,
)

PERSONA_LABELS = {
    PersonaType.MELCHIOR: "MELCHIOR",
    PersonaType.BALTHASAR: "BALTHASAR",
    PersonaType.CASPER: "CASPER",
}

PERSONA_ORDER = [PersonaType.MELCHIOR, PersonaType.BALTHASAR, PersonaType.CASPER]

DECISION_LABELS = {
    Decision.APPROVED: "✅ APPROVED",
    Decision.DENIED: "❌ DENIED",
    Decision.CONDITIONAL: "⚠️ CONDITIONAL",
}


class ReportGenerator:
    """Generate Markdown reports from ConsensusResult"""

    def __init__(self, result: ConsensusResult, prompt: str) -> None:
        """Initialize report generator
        
        Args:
            result: ConsensusResult from magi-core engine
            prompt: Original input prompt
        """
        self.result = result
        self.prompt = prompt
        self.generated_at = datetime.now()

    def generate(self) -> str:
        """Generate complete Markdown report
        
        Returns:
            Complete Markdown report as string
        """
        sections = [
            self._header(),
            self._input_section(),
            self._thinking_section(),
            self._debate_section(),
            self._voting_section(),
            self._decision_section(),
            self._footer(),
        ]
        return "\n\n".join(filter(None, sections))

    def _header(self) -> str:
        """Generate report header"""
        return "# MAGI System 合議結果レポート"

    def _input_section(self) -> str:
        """Generate input prompt section"""
        return f"## 入力\n\n```\n{self.prompt}\n```"

    def _thinking_section(self) -> str:
        """Generate thinking phase section"""
        lines = ["## Thinking Phase", ""]
        
        thinking = self.result.thinking_results
        for persona in PERSONA_ORDER:
            output = thinking.get(persona)
            label = PERSONA_LABELS[persona]
            lines.append(f"### {label}")
            if output and output.content:
                lines.append("")
                lines.append(output.content)
            else:
                lines.append("")
                lines.append("*No output produced.*")
            lines.append("")
        
        return "\n".join(lines)

    def _debate_section(self) -> str:
        """Generate debate phase section"""
        debate_results = self.result.debate_results
        if not debate_results:
            return "## Debate Phase\n\n*No debate rounds were produced.*"
        
        lines = ["## Debate Phase", ""]
        
        for round_data in debate_results:
            lines.append(f"### Round {round_data.round_number}")
            lines.append("")
            
            for persona in PERSONA_ORDER:
                output = round_data.outputs.get(persona)
                label = PERSONA_LABELS[persona]
                lines.append(f"#### {label}")
                
                if output is None:
                    lines.append("")
                    lines.append("*No response produced.*")
                    lines.append("")
                    continue
                
                responses = []
                for target, response in output.responses.items():
                    target_label = PERSONA_LABELS.get(target, str(target))
                    responses.append(f"**To {target_label}:** {response}")
                
                if responses:
                    lines.append("")
                    lines.extend(responses)
                else:
                    lines.append("")
                    lines.append("*No responses generated.*")
                lines.append("")
        
        return "\n".join(lines)

    def _voting_section(self) -> str:
        """Generate voting phase section"""
        lines = ["## Voting Phase", ""]
        
        # Build table header
        lines.append("| Persona | Vote | Reason | Conditions |")
        lines.append("|:--------|:----:|:-------|:-----------|")
        
        voting = self.result.voting_results
        for persona in PERSONA_ORDER:
            vote_output = voting.get(persona)
            label = PERSONA_LABELS[persona]
            
            if vote_output is None:
                lines.append(f"| {label} | N/A | No vote recorded. | |")
                continue
            
            vote_value = vote_output.vote.value.upper() if vote_output.vote else "N/A"
            reason = vote_output.reason or ""
            # Escape pipe characters in reason
            reason = reason.replace("|", "\\|")
            
            conditions = ""
            if vote_output.conditions:
                conditions = ", ".join(vote_output.conditions)
                conditions = conditions.replace("|", "\\|")
            
            lines.append(f"| {label} | {vote_value} | {reason} | {conditions} |")
        
        return "\n".join(lines)

    def _decision_section(self) -> str:
        """Generate final decision section"""
        decision = self.result.final_decision
        decision_label = DECISION_LABELS.get(decision, str(decision))
        
        lines = [
            "## Final Decision",
            "",
            f"**{decision_label}**",
        ]
        
        conditions = self.result.all_conditions
        if conditions:
            lines.append("")
            lines.append("### Conditions")
            lines.append("")
            for condition in conditions:
                lines.append(f"- {condition}")
        
        return "\n".join(lines)

    def _footer(self) -> str:
        """Generate report footer with metadata"""
        timestamp = self.generated_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"---\n\n*Generated by MAGI GUI at {timestamp}*"


def generate_report(result: ConsensusResult, prompt: str) -> str:
    """Convenience function to generate a report
    
    Args:
        result: ConsensusResult from magi-core engine
        prompt: Original input prompt
        
    Returns:
        Complete Markdown report as string
    """
    generator = ReportGenerator(result, prompt)
    return generator.generate()


def generate_filename(prompt: str, timestamp: Optional[datetime] = None) -> str:
    """Generate a filename for the report
    
    Args:
        prompt: Original input prompt (used for naming)
        timestamp: Optional timestamp, defaults to now
        
    Returns:
        Filename string like 'magi-report-20260108-155800.md'
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    date_str = timestamp.strftime("%Y%m%d-%H%M%S")
    return f"magi-report-{date_str}.md"
