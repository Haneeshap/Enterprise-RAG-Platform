# Enterprise RAG Platform - Day 1

## Project Structure
```
Enterprise RAG Platform/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── ingest.py
│   │   ├── query.py
│   │   ├── health.py
│   │   ├── metrics.py
│   │   └── auth.py
│   ├── auth/
│   │   └── jwt.py
│   ├── middleware/
│   │   ├── tenant.py
│   │   └── tracing.py
│   ├── models/
│   │   └── schemas.py
│   └── db/
│       ├── postgres.py
│       └── redis.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Routes

### POST /ingest
- Input: `{doc_id: str, text: str, metadata: dict, tenant_id: str}`
- Chunks text: 500 tokens, overlap 50, using tiktoken cl100k_base
- Generates embeddings: OpenAI text-embedding-3-small, mock: `[0.1]*1536` if no OPENAI_API_KEY
- Stores in Postgres pgvector
- Returns: `{doc_id, chunks: int, trace_id}`

```bash
curl -X POST "http://localhost:8000/ingest/" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant1" \
  -d '{"doc_id": "doc1", "text": "This is a test document about machine learning.", "metadata": {"source": "test"}}'
```

### POST /query
- Input: `{query: str, top_k: int=5, tenant_id: str}`
- Generates query embedding, searches pgvector cosine similarity
- Returns: `{answer, citations: [{doc_id, chunk_id, text, score}], trace_id, latency_ms}`

```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant1" \
  -d '{"query": "machine learning", "top_k": 3, "tenant_id": "tenant1"}'
```

### GET /health
- Returns: `{status: ok, db: up/down, redis: up/down, latency_ms, version: 1.0.0}`

```bash
curl "http://localhost:8000/health/"
```

### GET /metrics
- Prometheus metrics endpoint

```bash
curl "http://localhost:8000/metrics/"
```

### POST /auth/login
- Input: `{user_id, tenant_id}`
- Returns JWT HS256 expiry 1h: `{user_id, tenant_id, exp}`

```bash
curl -X POST "http://localhost:8000/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "tenant_id": "tenant1"}'
```

## Docker

```bash
docker-compose up -d
```

Check logs: `docker-compose logs -f app`

## Running Tests

```bash
pytest tests/test_day1.py -v
```

## Prometheus

Metrics available at `http://localhost:8000/metrics/`

Grafana can scrape metrics from: `http://localhost:8000/metrics`