"""MAGI GUI - Streamlit application"""
import asyncio
import html
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING

import streamlit as st

from magi.errors import MagiException
from magi.models import Attachment, Decision, DebateRound, PersonaType, ThinkingOutput, VoteOutput

if TYPE_CHECKING:
    from magi.config import Config
    from magi.core.consensus import ConsensusEngine
    from magi.models import ConsensusResult

from magi_gui.report import generate_report, generate_filename
from magi_gui.streaming_adapter import StreamlitStreamingAdapter

PERSONA_ORDER = [PersonaType.MELCHIOR, PersonaType.BALTHASAR, PersonaType.CASPER]
PERSONA_LABELS = {
    PersonaType.MELCHIOR: "MELCHIOR",
    PersonaType.BALTHASAR: "BALTHASAR",
    PersonaType.CASPER: "CASPER",
}
PERSONA_CLASSES = {
    PersonaType.MELCHIOR: "persona-melchior",
    PersonaType.BALTHASAR: "persona-balthasar",
    PersonaType.CASPER: "persona-casper",
}
DECISION_CLASSES = {
    Decision.APPROVED: "decision-approved",
    Decision.DENIED: "decision-denied",
    Decision.CONDITIONAL: "decision-conditional",
}


def _set_gemini_env(api_key: str, model: str, endpoint: str) -> None:
    """Set environment variables for Gemini provider"""
    os.environ["MAGI_DEFAULT_PROVIDER"] = "gemini"
    os.environ["MAGI_API_KEY"] = api_key
    os.environ["MAGI_MODEL"] = model
    os.environ["MAGI_GEMINI_API_KEY"] = api_key
    os.environ["MAGI_GEMINI_MODEL"] = model
    os.environ["MAGI_GEMINI_ENDPOINT"] = endpoint


def _load_css() -> None:
    """Load custom CSS styles"""
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _build_engine(config: "Config", streaming_emitter=None) -> "ConsensusEngine":
    """Build ConsensusEngine instance
    
    Args:
        config: Configuration object
        streaming_emitter: Optional streaming emitter for real-time output
    """
    from magi.core.consensus import ConsensusEngine
    return ConsensusEngine(config, streaming_emitter=streaming_emitter)


def _execute_async(
    engine: "ConsensusEngine",
    prompt: str,
    adapter: Optional["StreamlitStreamingAdapter"] = None,
    attachments: Optional[list[Attachment]] = None,
) -> "ConsensusResult":
    """Execute consensus engine asynchronously

    Args:
        engine: ConsensusEngine instance
        prompt: User prompt
        adapter: Optional streaming adapter
        attachments: Optional list of Attachment objects for multimodal input
    """

    async def _run():
        try:
            return await engine.execute(prompt, attachments=attachments)
        finally:
            if adapter:
                await adapter.close()

    return asyncio.run(_run())


def _normalize_thinking(thinking_results) -> Dict[PersonaType, ThinkingOutput]:
    """Normalize thinking results to use PersonaType keys"""
    normalized: Dict[PersonaType, ThinkingOutput] = {}
    for key, value in thinking_results.items():
        if isinstance(key, PersonaType):
            normalized[key] = value
            continue
        if isinstance(key, str):
            for persona in PersonaType:
                if persona.value == key:
                    normalized[persona] = value
                    break
    return normalized


def _normalize_votes(voting_results) -> Dict[PersonaType, VoteOutput]:
    """Normalize voting results to use PersonaType keys"""
    normalized: Dict[PersonaType, VoteOutput] = {}
    for key, value in voting_results.items():
        if isinstance(key, PersonaType):
            normalized[key] = value
            continue
        if isinstance(key, str):
            for persona in PersonaType:
                if persona.value == key:
                    normalized[persona] = value
                    break
    return normalized


def _render_persona_block(title: str, css_class: str, content: str) -> None:
    """Render a persona card block"""
    safe_content = html.escape(content or "")
    st.markdown(
        f"<div class='persona-card {css_class}'>"
        f"<div class='persona-title'>{title}</div>"
        f"<pre class='persona-content'>{safe_content}</pre>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_thinking(thinking_results: Dict[PersonaType, ThinkingOutput]) -> None:
    """Render thinking phase results in 3 columns"""
    cols = st.columns(3)
    for col, persona in zip(cols, PERSONA_ORDER):
        output = thinking_results.get(persona)
        content = output.content if output else "No output produced."
        label = PERSONA_LABELS[persona]
        css_class = PERSONA_CLASSES[persona]
        with col:
            _render_persona_block(label, css_class, content)


def _render_debate_round(round_data: DebateRound) -> None:
    """Render a single debate round"""
    for persona in PERSONA_ORDER:
        output = round_data.outputs.get(persona)
        label = PERSONA_LABELS[persona]
        css_class = PERSONA_CLASSES[persona]
        if output is None:
            _render_persona_block(label, css_class, "No response produced.")
            continue
        responses = []
        for target, response in output.responses.items():
            target_name = PERSONA_LABELS.get(target, str(target))
            responses.append(f"To {target_name}: {response}")
        content = "\n\n".join(responses) if responses else "No responses generated."
        _render_persona_block(label, css_class, content)


def _render_voting_table(voting_results: Dict[PersonaType, VoteOutput]) -> None:
    """Render voting results as a table"""
    rows = []
    for persona in PERSONA_ORDER:
        vote_output = voting_results.get(persona)
        if vote_output is None:
            rows.append(
                {
                    "Persona": PERSONA_LABELS[persona],
                    "Vote": "N/A",
                    "Reason": "No vote recorded.",
                    "Conditions": "",
                }
            )
            continue
        vote_value = vote_output.vote.value if vote_output.vote else "N/A"
        conditions = ""
        if vote_output.conditions:
            conditions = " | ".join(vote_output.conditions)
        rows.append(
            {
                "Persona": PERSONA_LABELS[persona],
                "Vote": vote_value.upper(),
                "Reason": vote_output.reason,
                "Conditions": conditions,
            }
        )
    st.table(rows)


def _render_final_decision(decision: Decision, conditions) -> None:
    """Render the final decision banner"""
    css_class = DECISION_CLASSES.get(decision, "decision-conditional")
    st.markdown(
        f"<div class='decision-banner {css_class}'>Final Decision: {decision.value.upper()}</div>",
        unsafe_allow_html=True,
    )
    if conditions:
        st.markdown("<div class='decision-conditions'>Conditions:</div>", unsafe_allow_html=True)
        for item in conditions:
            st.markdown(f"- {item}")


def _render_download_button(result: "ConsensusResult", prompt: str) -> None:
    """Render report download button"""
    report_content = generate_report(result, prompt)
    filename = generate_filename(prompt)
    
    st.download_button(
        label="📥 Download Report (Markdown)",
        data=report_content,
        file_name=filename,
        mime="text/markdown",
        key="download_report",
    )


def _render_error_message(exc: MagiException) -> str:
    """Format MagiException for display"""
    error = getattr(exc, "error", None)
    if error is None:
        return f"Magi error: {exc}"
    code = getattr(error, "code", "MAGI_ERROR")
    message = getattr(error, "message", str(exc))
    return f"{code}: {message}"


def _init_session_state() -> None:
    """Initialize session state variables"""
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.environ.get("MAGI_GEMINI_API_KEY", "")
    if "model" not in st.session_state:
        st.session_state.model = "gemini-1.5-pro"
    if "debate_rounds" not in st.session_state:
        st.session_state.debate_rounds = 3
    if "enable_streaming" not in st.session_state:
        st.session_state.enable_streaming = False
    if "result" not in st.session_state:
        st.session_state.result = None
    if "error" not in st.session_state:
        st.session_state.error = None


def run_app() -> None:
    """Main application entry point"""
    st.set_page_config(
        page_title="MAGI SYSTEM",
        page_icon="M",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _load_css()
    _init_session_state()

    st.markdown("<div class='app-title'>MAGI SYSTEM</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Triadic consensus with Gemini.</div>",
        unsafe_allow_html=True,
    )

    # Sidebar configuration
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>Configuration</div>", unsafe_allow_html=True)
        api_key = st.text_input(
            "Gemini API key",
            type="password",
            value=st.session_state.api_key,
            key="api_key_input",
        )
        model = st.selectbox(
            "Gemini model",
            options=["gemini-1.5-pro", "gemini-1.5-flash"],
            index=0 if st.session_state.model == "gemini-1.5-pro" else 1,
            key="model_select",
        )
        debate_rounds = st.slider(
            "Debate rounds",
            min_value=1,
            max_value=5,
            value=st.session_state.debate_rounds,
            key="debate_rounds_slider",
        )
        enable_streaming = st.checkbox(
            "Enable streaming (experimental)",
            value=st.session_state.enable_streaming,
            key="streaming_checkbox",
            help="Display debate output in real-time as it's generated",
        )
        
        # File uploader for multimodal input
        st.markdown("<div class='sidebar-subtitle'>Attachments</div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Attach files (PDF, Images)",
            accept_multiple_files=True,
            type=["pdf", "png", "jpg", "jpeg", "gif", "webp"],
            key="file_uploader",
            help="Attach PDF or image files for multimodal analysis (max 10MB each)",
        )

    # Main input area
    st.markdown("<div class='section-title'>Input</div>", unsafe_allow_html=True)
    prompt = st.text_area("Prompt", height=200, placeholder="Describe the decision to evaluate.")
    run_clicked = st.button("INITIALIZE", type="primary")

    if not run_clicked:
        return

    # Validation
    if not api_key:
        st.error("Please provide a Gemini API key to continue.")
        return
    if not prompt.strip():
        st.error("Please enter a prompt to run.")
        return

    # File size validation and Attachment conversion
    MAX_FILE_SIZE_MB = 10
    attachments = None
    if uploaded_files:

        
        attachments = []
        for f in uploaded_files:
            if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error(f"File '{f.name}' exceeds {MAX_FILE_SIZE_MB}MB limit.")
                return
            attachments.append(
                Attachment(
                    mime_type=f.type,
                    data=f.read(),
                    filename=f.name,
                )
            )
        # Reset file pointers after reading
        for f in uploaded_files:
            f.seek(0)

    # Set environment variables for Gemini
    endpoint = "https://generativelanguage.googleapis.com"
    _set_gemini_env(api_key, model, endpoint)

    # Import and create Config after env vars are set
    from magi.config.manager import Config
    
    try:
        config = Config(api_key=api_key, debate_rounds=int(debate_rounds), model=model)
    except MagiException as exc:
        st.error(_render_error_message(exc))
        return
    except Exception as exc:
        st.error(f"Configuration error: {exc}")
        return

    # Prepare streaming emitter if enabled
    streaming_emitter = None
    adapter = None
    stream_placeholders = {}
    if enable_streaming:
        # Create placeholders for each persona
        st.markdown("<div class='section-title'>Debate (Streaming)</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, persona in enumerate(PERSONA_ORDER):
            with cols[idx]:
                st.markdown(
                    f"<div class='persona-title' style='color: var(--{persona.value.lower()})'>{PERSONA_LABELS[persona]}</div>",
                    unsafe_allow_html=True,
                )
                stream_placeholders[persona] = st.empty()
        
        # Clear previous streaming state
        for persona in PERSONA_ORDER:
            key = f"stream_{persona.value}"
            if key in st.session_state:
                del st.session_state[key]
            stream_placeholders[persona].empty()

        # Create streaming adapter
        def on_chunk(chunk):
            """Handle streaming chunk - update placeholders"""
            # Find matching persona
            for persona in PERSONA_ORDER:
                if chunk.persona == persona.value and chunk.phase == "debate":
                    placeholder = stream_placeholders.get(persona)
                    if placeholder:
                        # Append chunk to existing content
                        key = f"stream_{persona.value}"
                        if key not in st.session_state:
                            st.session_state[key] = []
                        st.session_state[key].append(chunk.chunk)
                        combined = "\n\n".join(st.session_state[key])
                        placeholder.markdown(f"```\n{combined}\n```")
        
        adapter = StreamlitStreamingAdapter(on_chunk=on_chunk)
        streaming_emitter = adapter.create_emitter()

    try:
        engine = _build_engine(config, streaming_emitter=streaming_emitter)
    except MagiException as exc:
        st.error(_render_error_message(exc))
        return
    except Exception as exc:
        st.error(f"Engine initialization error: {exc}")
        return

    status_placeholder = st.empty()
    status_placeholder.info("Running consensus engine...")

    with st.spinner("Running..."):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_execute_async, engine, prompt, adapter, attachments)
                result = future.result()
        except MagiException as exc:
            status_placeholder.empty()
            st.error(_render_error_message(exc))
            return
        except Exception as exc:
            status_placeholder.empty()
            st.error(f"Unexpected error: {exc}")
            return

    status_placeholder.success("Completed.")

    thinking_results = _normalize_thinking(result.thinking_results)
    voting_results = _normalize_votes(result.voting_results)

    # Render Thinking phase
    st.markdown("<div class='section-title'>Thinking</div>", unsafe_allow_html=True)
    _render_thinking(thinking_results)

    # Render Debate phase
    st.markdown("<div class='section-title'>Debate</div>", unsafe_allow_html=True)
    if not result.debate_results:
        st.markdown("No debate rounds were produced.")
    else:
        for round_data in result.debate_results:
            with st.expander(f"Round {round_data.round_number}", expanded=False):
                _render_debate_round(round_data)

    # Render Voting phase
    st.markdown("<div class='section-title'>Voting</div>", unsafe_allow_html=True)
    _render_voting_table(voting_results)

    # Render Final Decision
    st.markdown("<div class='section-title'>Final Decision</div>", unsafe_allow_html=True)
    _render_final_decision(result.final_decision, result.all_conditions)

    # Report download section
    st.markdown("<div class='section-title'>Export</div>", unsafe_allow_html=True)
    _render_download_button(result, prompt)


# Streamlit entry point
if __name__ == "__main__":
    run_app()
