import hashlib
import json
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
DEFAULT_TTL = 3600

_r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def get_cache_key(tenant_id: str, query_hash: str) -> str:
    return f"{tenant_id}:{query_hash}"


def get_cache(key: str) -> dict | None:
    try:
        data = _r.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


def set_cache(key: str, value: dict, ttl: int = DEFAULT_TTL) -> bool:
    try:
        _r.setex(key, ttl, json.dumps(value))
        return True
    except Exception:
        return False


def delete_cache(key: str) -> bool:
    try:
        _r.delete(key)
        return True
    except Exception:
        return False


def compute_query_hash(query: str, top_k: int) -> str:
    combined = f"{query}{top_k}"
    return hashlib.md5(combined.encode()).hexdigest()
''')

with open("c:/Users/hanee/Enterprise RAG Platform/app/cache/redis.py", "w") as f:
    pass

print("Created redis.py placeholder")