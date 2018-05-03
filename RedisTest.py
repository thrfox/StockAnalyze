import json
from datetime import datetime

import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
"""
# String字符
r.set('test', 'testStr')
print(r['test'])

# Hash
r.delete('stocks')
l = [{'high': '100'}, {'low': '99'}]
scale = '5'
r.hset('stocks', 'sh:'+scale+':data', json.dumps(l))
l = [{'high': '199'}, {'low': '188'}]
scale = '240'
r.hset('stocks', 'sh:'+scale+':data', l)

# 将code 与dataList关联

alldata = r.hget('stocks', 'sh:5:data')
print(alldata)
result = json.loads(alldata)
print(type(alldata))
print(type(result))
alldata = r.hget('stocks', 'sh:240:data')
print(alldata)
print(r.hgetall('stocks'))

# test parse
start = datetime.now()
with open('sh600000.json', 'r') as js:
    e = json.load(js)
    print(e['data'])
data = eval(e['data'])
days = []
high = []
for day in data:
    days.append(day['day'])
    high.append(day['high'])
print(days)
print(high)
print(datetime.now() - start)
"""
print(r.hget('stocks-5', 'stocks:sh600000:5'))
