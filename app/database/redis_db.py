import redis
from configs.config import settings


redis_db = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DATABASE,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)
