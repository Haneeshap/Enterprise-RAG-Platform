{{ config(materialized='view') }}

SELECT
    id::text AS id,
    tenant_id::text AS tenant_id,
    doc_id::text AS doc_id,
    chunk_id::int AS chunk_id,
    text::text AS text,
    metadata::jsonb AS metadata,
    created_at::timestamp AS created_at
FROM docs