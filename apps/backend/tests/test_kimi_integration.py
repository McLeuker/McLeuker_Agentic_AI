"""
Tests for Kimi K2.5 Client
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.core.kimi_client import KimiClient, KimiResponse
from src.config.settings import settings


class TestKimiClient:
    """Test suite for Kimi K2.5 client."""
    
    @pytest.fixture
    def kimi_client(self):
        """Create Kimi client instance for testing."""
        with patch.object(settings, 'MOONSHOT_API_KEY', 'test_key'):
            return KimiClient()
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, kimi_client):
        """Test that client initializes correctly."""
        assert kimi_client.api_key == 'test_key'
        assert kimi_client.model == settings.KIMI_MODEL
        assert kimi_client.api_base == settings.KIMI_API_BASE
    
    @pytest.mark.asyncio
    async def test_execute_success(self, kimi_client):
        """Test successful execution."""
        mock_response = {
            'choices': [{
                'message': {
                    'content': 'Test response',
                    'tool_calls': []
                }
            }],
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 50,
                'total_tokens': 150
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            
            response = await kimi_client.execute("Test query")
            
            assert response.success is True
            assert response.content == 'Test response'
            assert response.tokens_used == 150
            assert response.model == settings.KIMI_MODEL
    
    @pytest.mark.asyncio
    async def test_execute_with_context(self, kimi_client):
        """Test execution with context."""
        query = "Generate code"
        context = "Previous conversation context"
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={
                'choices': [{'message': {'content': 'Code generated'}}],
                'usage': {'total_tokens': 200}
            })
            
            response = await kimi_client.execute(query, context=context)
            
            assert response.success is True
            assert 'Code generated' in response.content
    
    @pytest.mark.asyncio
    async def test_cost_calculation(self, kimi_client):
        """Test cost calculation."""
        input_tokens = 1_000_000  # 1M tokens
        output_tokens = 500_000   # 500K tokens
        
        cost = kimi_client._calculate_cost(input_tokens, output_tokens)
        
        # Expected: (1M * 0.002) + (0.5M * 0.006) = 2 + 3 = $5
        assert cost == pytest.approx(5.0, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, kimi_client):
        """Test error handling."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 500
            mock_post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Server error")
            
            response = await kimi_client.execute("Test query")
            
            assert response.success is False
            assert response.error is not None
    
    def test_needs_execution_detection(self):
        """Test execution need detection."""
        from src.core.hybrid_brain import HybridBrain
        
        brain = HybridBrain()
        
        # Should need execution
        assert brain._needs_execution("Generate Python code for data analysis")
        assert brain._needs_execution("Create an Excel report")
        assert brain._needs_execution("Build a script to process files")
        
        # Should not need execution
        assert not brain._needs_execution("What is fashion?")
        assert not brain._needs_execution("Explain the trend")


class TestHybridBrain:
    """Test suite for Hybrid Brain."""
    
    @pytest.fixture
    def hybrid_brain(self):
        """Create hybrid brain instance."""
        from src.core.hybrid_brain import HybridBrain
        return HybridBrain()
    
    @pytest.mark.asyncio
    async def test_reasoning_only(self, hybrid_brain):
        """Test pure reasoning workflow."""
        from src.core.hybrid_brain import TaskType
        
        with patch.object(hybrid_brain, 'grok') as mock_grok:
            mock_grok.think = AsyncMock(return_value=Mock(
                success=True,
                content="Reasoning response",
                reasoning=["Step 1"],
                error=None
            ))
            
            response = await hybrid_brain.think(
                "What is fashion?",
                task_type=TaskType.REASONING
            )
            
            assert response.success is True
            assert "grok" in response.models_used
            assert "kimi" not in response.models_used
    
    @pytest.mark.asyncio
    async def test_execution_only(self, hybrid_brain):
        """Test pure execution workflow."""
        from src.core.hybrid_brain import TaskType
        
        with patch.object(hybrid_brain, 'kimi') as mock_kimi:
            mock_kimi.execute = AsyncMock(return_value=Mock(
                success=True,
                content="Code generated",
                reasoning=["Executed"],
                tool_calls=None,
                tokens_used=100,
                cost=0.001,
                error=None
            ))
            
            response = await hybrid_brain.think(
                "Generate Python code",
                task_type=TaskType.EXECUTION
            )
            
            assert response.success is True
            assert "kimi" in response.models_used
    
    @pytest.mark.asyncio
    async def test_hybrid_workflow(self, hybrid_brain):
        """Test hybrid workflow with both models."""
        from src.core.hybrid_brain import TaskType
        
        with patch.object(hybrid_brain, 'grok') as mock_grok, \
             patch.object(hybrid_brain, 'kimi') as mock_kimi:
            
            mock_grok.think = AsyncMock(return_value=Mock(
                success=True,
                content="Plan created",
                reasoning=["Planning"],
                error=None
            ))
            
            mock_kimi.execute = AsyncMock(return_value=Mock(
                success=True,
                content="Executed",
                reasoning=["Execution"],
                tool_calls=None,
                tokens_used=100,
                cost=0.001,
                error=None
            ))
            
            response = await hybrid_brain.think(
                "Generate fashion trend report",
                task_type=TaskType.HYBRID
            )
            
            assert response.success is True
            assert "grok" in response.models_used
            assert "kimi" in response.models_used


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
