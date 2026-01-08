"""Tests for magi_gui.streaming_adapter module"""
import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest

from magi.core.streaming import StreamChunk
from magi.models import PersonaType
from magi_gui.streaming_adapter import (
    StreamlitStreamingAdapter,
    create_streamlit_emitter,
)


class TestStreamlitStreamingAdapter:
    """Tests for StreamlitStreamingAdapter class"""

    def test_init_sets_callback(self):
        """__init__() should store callback function"""
        callback = MagicMock()
        
        adapter = StreamlitStreamingAdapter(on_chunk=callback)
        
        assert adapter.on_chunk is callback

    def test_init_sets_queue_params(self):
        """__init__() should store queue parameters"""
        adapter = StreamlitStreamingAdapter(
            on_chunk=MagicMock(),
            queue_size=50,
            emit_timeout_seconds=1.5,
        )
        
        assert adapter._queue_size == 50
        assert adapter._emit_timeout == 1.5

    def test_create_emitter_returns_queue_emitter(self):
        """create_emitter() should return QueueStreamingEmitter"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        
        emitter = adapter.create_emitter()
        
        assert emitter is not None
        assert hasattr(emitter, "emit")
        assert hasattr(emitter, "start")
        assert hasattr(emitter, "aclose")

    @pytest.mark.asyncio
    async def test_send_chunk_calls_callback(self):
        """_send_chunk() should call user callback"""
        callback = MagicMock()
        adapter = StreamlitStreamingAdapter(on_chunk=callback)
        
        chunk = StreamChunk(
            persona="melchior",
            chunk="Test content",
            phase="debate",
            round_number=1,
        )
        
        await adapter._send_chunk(chunk)
        
        callback.assert_called_once_with(chunk)

    @pytest.mark.asyncio
    async def test_send_chunk_stores_chunk(self):
        """_send_chunk() should store chunk by phase"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        
        chunk = StreamChunk(
            persona="melchior",
            chunk="Test content",
            phase="debate",
            round_number=1,
        )
        
        await adapter._send_chunk(chunk)
        
        assert "debate" in adapter._chunks
        assert chunk in adapter._chunks["debate"]

    def test_get_chunks_by_phase_returns_list(self):
        """get_chunks_by_phase() should return stored chunks"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        chunk = StreamChunk(
            persona="melchior",
            chunk="Test",
            phase="thinking",
        )
        adapter._chunks["thinking"].append(chunk)
        
        result = adapter.get_chunks_by_phase("thinking")
        
        assert result == [chunk]

    def test_get_chunks_by_phase_case_insensitive(self):
        """get_chunks_by_phase() should be case insensitive"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        chunk = StreamChunk(
            persona="melchior",
            chunk="Test",
            phase="debate",
        )
        adapter._chunks["debate"].append(chunk)
        
        result = adapter.get_chunks_by_phase("DEBATE")
        
        assert result == [chunk]

    def test_get_chunks_by_persona_filters_correctly(self):
        """get_chunks_by_persona() should filter by persona"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        chunk1 = StreamChunk(
            persona="melchior",
            chunk="Test 1",
            phase="debate",
        )
        chunk2 = StreamChunk(
            persona="balthasar",
            chunk="Test 2",
            phase="debate",
        )
        adapter._chunks["debate"].extend([chunk1, chunk2])
        
        result = adapter.get_chunks_by_persona(PersonaType.MELCHIOR, "debate")
        
        assert len(result) == 1
        assert result[0] == chunk1

    @pytest.mark.asyncio
    async def test_close_calls_emitter_aclose(self):
        """close() should close the emitter"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        emitter = adapter.create_emitter()
        adapter._emitter = emitter
        
        # Mock aclose
        emitter.aclose = AsyncMock()
        
        await adapter.close()
        
        emitter.aclose.assert_called_once()

    def test_dropped_returns_emitter_dropped(self):
        """dropped property should return emitter's dropped count"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        emitter = adapter.create_emitter()
        adapter._emitter = emitter
        
        # Emitter should start with 0 dropped
        assert adapter.dropped == 0

    def test_dropped_returns_zero_when_no_emitter(self):
        """dropped property should return 0 when no emitter"""
        adapter = StreamlitStreamingAdapter(on_chunk=MagicMock())
        
        assert adapter.dropped == 0


class TestCreateStreamlitEmitter:
    """Tests for create_streamlit_emitter convenience function"""

    def test_returns_queue_emitter(self):
        """create_streamlit_emitter() should return QueueStreamingEmitter"""
        callback = MagicMock()
        
        emitter = create_streamlit_emitter(on_chunk=callback)
        
        assert emitter is not None
        assert hasattr(emitter, "emit")

    def test_passes_parameters(self):
        """create_streamlit_emitter() should pass parameters to adapter"""
        callback = MagicMock()
        
        emitter = create_streamlit_emitter(
            on_chunk=callback,
            queue_size=50,
            emit_timeout_seconds=1.5,
        )
        
        # Emitter should be created successfully with custom params
        assert emitter is not None


class TestStreamingIntegration:
    """Integration tests for streaming adapter"""

    @pytest.mark.asyncio
    async def test_emitter_calls_adapter_callback(self):
        """Emitter should trigger adapter callback when emitting"""
        collected_chunks = []
        
        def callback(chunk):
            collected_chunks.append(chunk)
        
        adapter = StreamlitStreamingAdapter(on_chunk=callback)
        emitter = adapter.create_emitter()
        
        await emitter.start()
        await emitter.emit("melchior", "Test chunk", "debate", 1)
        
        # Give async queue time to process
        await asyncio.sleep(0.1)
        
        assert len(collected_chunks) > 0
        assert collected_chunks[0].persona == "melchior"
        assert collected_chunks[0].chunk == "Test chunk"
        
        await emitter.aclose()
