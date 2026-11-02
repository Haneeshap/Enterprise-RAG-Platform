{{ config(materialized='table') }}

SELECT
    tenant_id::text AS tenant_id,
    doc_id::text AS doc_id,
    COUNT(*) AS chunks,
    AVG(LENGTH(text)::float) AS avg_length
FROM stg_docs
GROUP BY tenant_id, doc_id