# Runbook: Enterprise RAG Platform SLI/SLO Monitoring

## Overview
This runbook describes the SLO monitoring and incident response for the Enterprise RAG Platform.

## SLO Definition
- **SLO Name**: rag_platform_slo
- **Error Budget**: 0.1% (1000 errors per 1,000,000 requests)
- **Availability Target**: 99.9%
- **Latency P95 Target**: <500ms

## SLIs Monitored
1. **latency_p95**: 95th percentile of request latency (target: <500ms)
2. **availability**: Ratio of successful requests to total requests (target: 99.9%)
3. **throughput**: Requests per second (monitoring only)

## Incident Response

### When Error Budget is Exceeded (>90% consumed):
1. Investigate latency spikes using Grafana dashboards
2. Check for increased error rates in /auth/stats and /audit endpoints
3. Review recent deployments or configuration changes
4. Contact on-call if error budget is 50% consumed or below

### When Latency P95 > 500ms:
1. Check Redis cache hit rate - low cache hits increase latency
2. Inspect pgvector HNSW index performance
3. Check Kafka consumer lag if ingest pipeline is backing up
4. Review recent query patterns for anomalies

### Recovery Procedures:
- **Cache miss spike**: Investigate Redis connectivity, check for memory pressure
- **Database performance**: Review pgvector index health, check for long-running queries
- **Kafka backpressure**: Monitor consumer lag, adjust producer rates

## Monitoring Commands

```bash
# Check error budget remaining
curl http://localhost:8000/slo/status

# View current metrics
curl http://localhost:9090/metrics | grep sla_

# Alert status
curl http://localhost:9093/api/v1/rules | jq .
```
```

Now let me create the test files.</think>
<tool_call>
<function=editor>
<parameter=new_text>
"""Day 7 tests for Enterprise RAG Platform - RLS, audit, rate limiting."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rls_tenant_isolation():
    """Test that tenant A cannot query tenant B docs."""
    # Create doc under tenant A
    client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "Secret tenant A document", "metadata": {}, "tenant_id": "tenant_a"},
    )
    
    # Tenant B should not be able to query it (RLS 403)
    response = client.post(
        "/query/",
        json={"query": "secret", "top_k": 3, "tenant_id": "tenant_b"},
    )
    assert response.status_code == 403


def test_audit_log_ingest():
    """Test that ingest operations are logged."""
    response = client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "Test document", "metadata": {"source": "test"}, "tenant_id": "tenant1"},
    )
    assert response.status_code == 200
    
    # Check audit logs
    response = client.get("/audit?tenant_id=tenant1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) > 0
    assert data["logs"][0]["action"] == "ingest"
    assert "trace_id" in data["logs"][0]


def test_rate_limit_429():
    """Test that 101st request returns 429."""
    # Make 100 successful auth requests
    for i in range(100):
        response = client.post(
            "/auth/login/",
            json={"user_id": f"user{i}", "tenant_id": "tenant1"},
        )
        assert response.status_code == 200
    
    # 101st should be rate limited
    response = client.post("/auth/login/", json={"user_id": "user101", "tenant_id": "tenant1"})
    assert response.status_code == 429


def test_auth_stats():
    """Test auth stats endpoint returns metrics."""
    response = client.get("/auth/stats?tenant_id=tenant1")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "failure" in data
    assert "rate_limit_hits" in data


def test_cross_tenant_audit_isolation():
    """Test that audit logs are isolated per tenant."""
    # Create activity under tenant A
    client.post(
        "/ingest/",
        json={"doc_id": "doc1", "text": "Tenant A document", "metadata": {}, "tenant_id": "tenant_a"},
    )
    
    # Create activity under tenant B
    client.post(
        "/ingest/",
        json={"doc_id": "doc2", "text": "Tenant B document", "metadata": {}, "tenant_id": "tenant_b"},
    )
    
    # Check tenant A logs only contain tenant A activity
    response = client.get("/audit?tenant_id=tenant_a")
    data = response.json()
    assert len(data["logs"]) > 0
    for log in data["logs"]:
        assert log["tenant_id"] == "tenant_a"