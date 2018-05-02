import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)

# String字符
r.set('test', 'testStr')
print(r['test'])

# Hash
r.delete('stocks')
l = [{'high': '100'}, {'low': '99'}]
scale = '5'
r.hset('stocks', 'sh:'+scale+':data', l)
l = [{'high': '199'}, {'low': '188'}]
scale = '240'
r.hset('stocks', 'sh:'+scale+':data', l)

# 将code 与dataList关联

alldata = r.hget('stocks', 'sh:5:data')
print(alldata)
alldata = r.hget('stocks', 'sh:240:data')
print(type(alldata.decode('utf-8')))
print(r.hgetall('stocks'))

