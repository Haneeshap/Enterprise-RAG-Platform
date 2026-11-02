# Cost Report - RAG Platform

## Cost per 1k Queries
- **Without cache**: $0.50 per 1k queries
- **With cache**: $0.20 per 1k queries
- **Cost cut**: 60%

## Breakdown
- **Embedding**: 10% ($0.05 per 1k queries)
- **LLM**: 80% ($0.40 per 1k queries)
- **Reranker**: 10% ($0.05 per 1k queries)

## Cache Hit Rate
- **Cache hit rate**: 60%
- **Cache saves**: $0.30 per 1k queries

## Optimization
- **Query cache**: tenant_id:query_hash -> {answer, citations}, TTL 1h
- **Embedding cache**: doc_id -> embedding, TTL 24h
- **Reranker cache**: query_hash + doc_ids hash -> reranked results

## Cost Summary (10k queries)
- **Without cache**: $5.00
- **With cache**: $2.00
- **Saved**: $3.00 (60% reduction)

## Graphs
- **Cost trend**: Daily cost over past 30 days
- **Cache hit vs cost**: Inverse correlation visualization
- **Tenant breakdown**: Cost per tenant analysis

## Recommendations
1. **Increase cache hit rate**: Target 65-70% for additional 10% cost cut
2. **Optimize embedding cache**: Cache doc embeddings for 24h to reduce embedding cost
3. **Monitor cost anomalies**: Set alerts for cost spikes >2x average
4. **Review LLM model**: Consider model downgrade if quality permits
5. **Query optimization**: Implement query caching for repeated queries