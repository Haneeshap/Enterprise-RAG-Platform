"""Day 2 tests for Enterprise RAG Platform - HNSW, EXPLAIN, data quality, window queries."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_hnsw_search_latency():
    """Test that HNSW search latency is <100ms."""
    # Ingest a document first
    client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "This is a test document for HNSW search testing.", "metadata": {"source": "test"}, "tenant_id": "tenant1"},
    )
    
    # Test HNSW stats endpoint
    response = client.post("/debug/hnsw-stats/", json={"tenant_id": "tenant1"})
    assert response.status_code == 200
    data = response.json()
    assert "m" in data
    assert "ef_construction" in data
    assert "index_type" in data
    assert "tenant_count" in data
    
    # Test explain endpoint
    response = client.post("/debug/explain/", json={"query": "machine learning", "tenant_id": "tenant1"})
    assert response.status_code == 200
    data = response.json()
    assert "explain" in data
    assert "execution_time_ms" in data
    assert "index_used" in data
    # Execution time should be reasonable
    assert data["execution_time_ms"] < 100


def test_explain_returns_planning_time():
    """Test that explain endpoint returns planning time."""
    response = client.post("/debug/explain/", json={"query": "test query", "tenant_id": "tenant1"})
    assert response.status_code == 200
    data = response.json()
    assert "planning_time_ms" in data
    assert "execution_time_ms" in data
    assert "index_used" in data


def test_data_quality_returns_coverage():
    """Test that data quality endpoint returns coverage percent."""
    response = client.get("/data-quality?tenant_id=tenant1")
    assert response.status_code == 200
    data = response.json()
    assert "coverage_percent" in data
    assert "total_docs" in data
    assert "null_count" in data
    assert "dim_mismatch_count" in data
    assert "avg_doc_length" in data
    assert "min_doc_length" in data
    assert "max_doc_length" in data


def test_window_query_last_7_days():
    """Test that window query returns last 7 days top docs."""
    # First ingest some documents and queries
    client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "Test document 1", "metadata": {}, "tenant_id": "tenant1"},
    )
    client.post(
        "/ingest/",
        json={"doc_id": "doc2", "text": "Test document 2", "metadata": {}, "tenant_id": "tenant1"},
    )
    
    # Add some audit log entries by querying
    client.post("/query/", json={"query": "test", "top_k": 3, "tenant_id": "tenant1"})
    client.post("/query/", json={"query": "test", "top_k": 3, "tenant_id": "tenant1"})
    client.post("/query/", json={"query": "other", "top_k": 3, "tenant_id": "tenant1"})
    
    # Test last_7_days_top_docs
    response = client.get("/analytics/window?type=last_7_days_top_docs&tenant_id=tenant1")
    assert response.status_code == 200
    data = response.json()
    assert "query_type" in data
    assert "results" in data
    assert "latency_ms" in data
    assert "trace_id" in data
    # Should return top 10 doc_ids
    assert isinstance(data["results"], list)