-- Migration: 001_hnsw.sql -- Create pgvector extension and HNSW indexes
-- Run: psql -U rag -d rag -f migrations/001_hnsw.sql

-- Create vector extension if not exists
CREATE EXTENSION IF NOT EXISTS vector;

-- Docs table (matching Day 1 schema with vector extension)
CREATE TABLE IF NOT EXISTS docs (
    id UUID PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    doc_id VARCHAR NOT NULL,
    chunk_id INT,
    text TEXT,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (tenant_id, doc_id, chunk_id)
);

-- Create indexes
-- HNSW index for cosine similarity search with m=16, ef_construction=64
CREATE INDEX IF NOT EXISTS docs_embedding_hnsw_idx ON docs USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);

-- Index for tenant isolation
CREATE INDEX IF NOT EXISTS docs_tenant_id_idx ON docs (tenant_id);

-- Index for doc_id lookups
CREATE INDEX IF NOT EXISTS docs_doc_id_idx ON docs (doc_id);

-- Slow query log table
CREATE TABLE IF NOT EXISTS slow_query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    query TEXT NOT NULL,
    execution_time_ms FLOAT NOT NULL,
    planning_time_ms FLOAT,
    trace_id VARCHAR,
    timestamp TIMESTAMP DEFAULT NOW(),
    index_used BOOLEAN DEFAULT FALSE
);

-- Add comment on HNSW index
COMMENT ON INDEX docs_embedding_hnsw_idx IS 'HNSW index for cosine similarity search on embedding vector';