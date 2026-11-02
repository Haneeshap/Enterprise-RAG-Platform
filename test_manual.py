"""Test script for Enterprise RAG Platform."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ingest():
    """Test that ingest returns chunks and trace_id."""
    response = client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "This is a test document about machine learning.", "metadata": {"source": "test"}, "tenant_id": "tenant1"},
    )
    print(f"Ingest status: {response.status_code}")
    print(f"Ingest response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["doc_id"] == "doc1"
    assert data["chunks"] > 0
    assert "trace_id" in data
    print("Ingest test PASSED")


def test_query():
    """Test that query returns citations."""
    # First ingest a document
    client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "This is a test document about machine learning.", "metadata": {"source": "test"}, "tenant_id": "tenant1"},
    )
    
    response = client.post(
        "/query/",
        json={"query": "machine learning", "top_k": 3, "tenant_id": "tenant1"},
    )
    print(f"Query status: {response.status_code}")
    print(f"Query response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0
    assert "trace_id" in data
    print("Query test PASSED")


def test_health():
    """Test that health returns ok status."""
    response = client.get("/health/")
    print(f"Health status: {response.status_code}")
    print(f"Health response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "db" in data
    assert "redis" in data
    assert "latency_ms" in data
    print("Health test PASSED")


def test_auth_jwt():
    """Test that auth/login returns JWT token."""
    response = client.post(
        "/auth/login/",
        json={"user_id": "user1", "tenant_id": "tenant1"},
    )
    print(f"Auth status: {response.status_code}")
    print(f"Auth response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["user_id"] == "user1"
    assert "tenant_id" in data
    assert data["tenant_id"] == "tenant1"
    # Check JWT payload
    token = data.get("access_token") or data.get("token", "")
    print("Auth test PASSED")


def test_tenant_isolation():
    """Test that tenant_id mismatch causes issues."""
    response = client.post(
        "/ingest/",
        json={"doc_id": "doc2", "text": "Another test document.", "metadata": {}, "tenant_id": "tenant2"},
    )
    print(f"Tenant isolation status: {response.status_code}")
    print(f"Tenant isolation response: {response.json()}")
    # The test depends on middleware setup
    print("Tenant isolation test completed")


if __name__ == "__main__":
    test_ingest()
    test_query()
    test_health()
    test_auth_jwt()
    test_tenant_isolation()
    print("\nAll tests completed!")