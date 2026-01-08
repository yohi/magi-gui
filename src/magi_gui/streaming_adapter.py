"""Streaming adapter for MAGI GUI

This module provides an adapter between magi-core's QueueStreamingEmitter
and Streamlit's UI components for real-time consensus output display.
"""
import asyncio
from typing import Callable, Dict, Optional

from magi.core.streaming import QueueStreamingEmitter, StreamChunk
from magi.models import PersonaType


class StreamlitStreamingAdapter:
    """Adapter for streaming consensus output to Streamlit UI
    
    This adapter wraps magi-core's QueueStreamingEmitter and provides
    hooks to update Streamlit placeholders in real-time.
    """

    def __init__(
        self,
        on_chunk: Callable[[StreamChunk], None],
        queue_size: int = 100,
        emit_timeout_seconds: float = 2.0,
    ) -> None:
        """Initialize streaming adapter
        
        Args:
            on_chunk: Callback function to handle each stream chunk
            queue_size: Maximum queue size for buffering chunks
            emit_timeout_seconds: Timeout for emitting each chunk
        """
        self.on_chunk = on_chunk
        self._emitter: Optional[QueueStreamingEmitter] = None
        self._queue_size = queue_size
        self._emit_timeout = emit_timeout_seconds
        self._chunks: Dict[str, list] = {
            "thinking": [],
            "debate": [],
            "voting": [],
        }

    async def _send_chunk(self, chunk: StreamChunk) -> None:
        """Send chunk to Streamlit UI (async callback for QueueStreamingEmitter)
        
        Args:
            chunk: Stream chunk from magi-core
        """
        # Store chunk for later retrieval
        phase = chunk.phase.lower()
        if phase in self._chunks:
            self._chunks[phase].append(chunk)
        
        # Call user-provided callback (must be sync)
        if self.on_chunk is not None:
            self.on_chunk(chunk)

    def create_emitter(self) -> QueueStreamingEmitter:
        """Create QueueStreamingEmitter instance
        
        Returns:
            Configured QueueStreamingEmitter for ConsensusEngine
        """
        self._emitter = QueueStreamingEmitter(
            send_func=self._send_chunk,
            queue_size=self._queue_size,
            emit_timeout_seconds=self._emit_timeout,
            auto_start=True,
        )
        return self._emitter

    def get_chunks_by_phase(self, phase: str) -> list:
        """Get all chunks for a specific phase
        
        Args:
            phase: Phase name (thinking, debate, voting)
            
        Returns:
            List of StreamChunk objects for the phase
        """
        return self._chunks.get(phase.lower(), [])

    def get_chunks_by_persona(self, persona: PersonaType, phase: str) -> list:
        """Get chunks for a specific persona and phase
        
        Args:
            persona: PersonaType to filter by
            phase: Phase name to filter by
            
        Returns:
            List of StreamChunk objects matching filters
        """
        chunks = self.get_chunks_by_phase(phase)
        return [c for c in chunks if c.persona == persona.value]

    async def close(self) -> None:
        """Close the streaming emitter"""
        if self._emitter is not None:
            await self._emitter.aclose()

    @property
    def dropped(self) -> int:
        """Get number of dropped chunks"""
        if self._emitter is not None:
            return self._emitter.dropped
        return 0


def create_streamlit_emitter(
    on_chunk: Callable[[StreamChunk], None],
    queue_size: int = 100,
    emit_timeout_seconds: float = 2.0,
) -> QueueStreamingEmitter:
    """Convenience function to create a streaming emitter for Streamlit
    
    Args:
        on_chunk: Callback to handle each stream chunk
        queue_size: Maximum queue size
        emit_timeout_seconds: Timeout per chunk
        
    Returns:
        Configured QueueStreamingEmitter instance
    """
    adapter = StreamlitStreamingAdapter(
        on_chunk=on_chunk,
        queue_size=queue_size,
        emit_timeout_seconds=emit_timeout_seconds,
    )
    return adapter.create_emitter()
