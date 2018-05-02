import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

# String字符
r.set('test', 'testStr')
print(r['test'])

# Hash
l = [{'t1': 't1'}, {'t2': 't2'}]
r.hset('dict', 'd', l)
r.hset('dict', 'ds', r.hget('dict', 'd'))
print(r.hget('dict', 'ds'))
print(r.hgetall('dict'))

