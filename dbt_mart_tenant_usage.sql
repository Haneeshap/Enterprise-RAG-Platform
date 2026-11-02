{{ config(materialized='table') }}

SELECT
    tenant_id::text AS tenant_id,
    COUNT(DISTINCT doc_id) AS docs,
    COUNT(*) AS chunks
FROM stg_docs
GROUP BY tenant_id