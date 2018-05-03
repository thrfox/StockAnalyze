import redis

DATASOURCE_HOST = '127.0.0.1'
DATASOURCE_PORT = 6379
DATASOURCE_POOL = redis.ConnectionPool(host=DATASOURCE_HOST, port=DATASOURCE_PORT, decode_responses=True)
