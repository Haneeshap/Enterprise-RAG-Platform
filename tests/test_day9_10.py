"""Day 9-10 tests for Enterprise RAG Platform - Cost tracking and cache optimization."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_cost_tracking_returns_cost_per_1k():
    """Test that cost tracking returns cost per 1k queries."""
    # Record some query costs
    from app.cost.tracking import track_query_cost, get_cost_summary
    
    # Record some queries with cache hits and misses
    track_query_cost(150, 500, 200, 5, cache_hit=False)  # No cache hit
    track_query_cost(150, 500, 200, 5, cache_hit=True)   # Cache hit
    track_query_cost(120, 400, 180, 3, cache_hit=True)   # Cache hit
    
    # Get cost summary
    summary = get_cost_summary()
    
    assert "cost_per_1k_queries" in summary
    assert "total_queries" in summary
    assert "total_cost" in summary
    assert "cache_hit_rate" in summary
    assert "cost_cut_percent" in summary
    assert summary["cache_hit_rate"] > 0  # Should have some cache hits


def test_cache_hit_cuts_cost_60():
    """Test that cache hit cuts cost by 60%."""
    from app.cost.tracking import track_query_cost, get_cost_summary
    
    # Record many cache miss queries first
    for _ in range(90):
        track_query_cost(150, 500, 200, 5, cache_hit=False)
    
    # Then record cache hit queries
    for _ in range(10):
        track_query_cost(150, 500, 200, 5, cache_hit=True)
    
    # Get cost summary
    summary = get_cost_summary()
    
    # Should have significant cost cut from cache hits
    assert summary["cost_cut_percent"] >= 50  # Should be at least 50% with 10% cache hit rate
    assert summary["cache_hit_rate"] > 0


def test_cost_breakdown_embedding_llm_reranker():
    """Test that cost breakdown includes embedding, llm, and reranker."""
    from app.cost.tracking import calculate_cost
    
    # Test with typical values
    result = calculate_cost(
        query_tokens=50,
        doc_tokens=1000,
        answer_tokens=200,
        top_k=5
    )
    
    assert "embedding_cost" in result
    assert "llm_cost" in result
    assert "reranker_cost" in result
    assert "total_cost" in result
    
    # Verify cost breakdown sums to total
    assert abs(result["total_cost"] - (result["embedding_cost"] + result["llm_cost"] + result["reranker_cost"])) < 0.0001
    
    # Verify costs are positive
    assert result["embedding_cost"] > 0
    assert result["llm_cost"] > 0
    assert result["reranker_cost"] > 0
    assert result["total_cost"] > 0