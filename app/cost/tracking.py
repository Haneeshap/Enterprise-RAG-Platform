import time
from datetime import datetime, timezone


def calculate_cost(
    embedding_tokens: int = 100,
    llm_tokens: int = 150,
    embedding_price_per_1k: float = 0.00002,
    llm_price_per_1k: float = 0.01,
) -> dict:
    """
    Calculate cost per query based on token usage.
    
    Args:
        embedding_tokens: Number of tokens in the query embedding
        llm_tokens: Number of tokens in the LLM response
        embedding_price_per_1k: Price per 1k embedding tokens
        llm_price_per_1k: Price per 1k LLM tokens
    
    Returns:
        dict with cost breakdown and totals
    """
    embedding_cost = (embedding_tokens / 1000) * embedding_price_per_1k
    llm_cost = (llm_tokens / 1000) * llm_price_per_1k
    total_cost = embedding_cost + llm_cost
    
    return {
        "embedding_cost": round(embedding_cost, 6),
        "llm_cost": round(llm_cost, 6),
        "total_cost": round(total_cost, 6),
        "tokens": {
            "embedding_tokens": embedding_tokens,
            "llm_tokens": llm_tokens,
            "total_tokens": embedding_tokens + llm_tokens,
        }
    }


def get_cost_per_1k_queries(
    queries_today: int = 0,
    total_cost_today: float = 0.0,
) -> dict:
    """
    Get cost per 1,000 queries.
    """
    if queries_today == 0:
        cost_per_1k = 0.0
    else:
        cost_per_1k = (total_cost_today / queries_today) * 1000
    
    return {
        "cost_per_1k_queries": round(cost_per_1k, 4),
        "queries_today": queries_today,
        "total_cost_today": round(total_cost_today, 4),
    }


def get_cost_breakdown(tenant_id: str = "") -> dict:
    """
    Get cost breakdown for a tenant.
    In production, this would query a cost tracking database.
    """
    # Mock data - in production, this would come from a database
    return {
        "tenant_id": tenant_id,
        "embedding_cost_per_query": 0.00002,
        "llm_cost_per_query": 0.01,
        "total_cost_per_query": 0.01002,
        "cache_hit_rate": 0.45,  # 45% cache hit rate
        "cost_cut_percent": 60.0,  # 60% cost cut from cache hits
    }