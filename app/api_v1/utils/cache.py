import aioredis
import json

redis = aioredis.from_url("redis://localhost")

async def cache_transaction_history(user_id: str, transactions: list):
    await redis.set(f"user:{user_id}:transactions", json.dumps(transactions), ex=3600)

async def get_cached_transaction_history(user_id: str):
    data = await redis.get(f"user:{user_id}:transactions")
    if data:
        return json.loads(data)
    return None
