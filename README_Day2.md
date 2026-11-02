# Enterprise RAG Platform - Day 2

## HNSW Index & EXPLAIN ANALYZE

### POST /debug/hnsw-stats
Returns HNSW index statistics including m, ef_construction, index_size, index_type, and tenant_count.

```bash
curl -X POST "http://localhost:8000/debug/hnsw-stats" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant1" \
  -d '{}'
```

### POST /debug/explain
Run EXPLAIN ANALYZE on a pgvector search query. Sets hnsw.ef_search=40 before query.

```bash
curl -X POST "http://localhost:8000/debug/explain" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant1" \
  -d '{"query": "machine learning", "tenant_id": "tenant1"}'
```

### GET /data-quality
Returns data quality metrics including doc length statistics, null embedding count, dim mismatch count, and embedding coverage.

```bash
curl "http://localhost:8000/data-quality?tenant_id=tenant1"
```

## Window Queries Analytics

### GET /analytics/window?type={type}&tenant_id={tenant_id}
Returns various window query analytics from audit_logs.

```bash
# Last 7 days top docs
curl "http://localhost:8000/analytics/window?type=last_7_days_top_docs&tenant_id=tenant1"

# Top queries
curl "http://localhost:8000/analytics/window?type=top_queries&tenant_id=tenant1"

# Latency p95
curl "http://localhost:8000/analytics/window?type=latency_p95&tenant_id=tenant1"

# Error rate
curl "http://localhost:8000/analytics/window?type=error_rate&tenant_id=tenant1"

# Tenant usage
curl "http://localhost:8000/analytics/window?type=tenant_usage&tenant_id=tenant1"
```