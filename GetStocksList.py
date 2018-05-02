import json
import multiprocessing
import re
from datetime import datetime
from multiprocessing.dummy import Pool
from urllib import request

import itertools

import redis

all_stocks_symbol_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/' \
                        'Market_Center.getHQNodeData?page=%s&num=100&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=init'


def get_stocks_symbol(page):
    """
    获取单个股票代码
    :return 股票dict
    """
    html = request.urlopen(all_stocks_symbol_url % page).read().decode('gbk')
    symbols = re.findall('(?:symbol|name):\"(.*?)\"', html)
    stocks = []
    for code, name in zip(*[iter(symbols)]*2):
        d = {code: name}
        stocks.append(d)
    if not stocks:
        raise IndexError
    return stocks


def start_spider():
    p = Pool(multiprocessing.cpu_count())
    print('***爬取所有股票代码中...***')
    stocks = []
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    count = 0
    for page in range(1, 36):
        print('正在爬取第', page, '页')
        l = p.apply_async(get_stocks_symbol, args=(page,))
        stocks.append(l)
    print('***爬取结束,录入中...***')
    start = datetime.now()
    for stock in stocks:
        for data in stock.get():
            (code, name), = data.items()
            r.hset('stocksCode', code, name)
            count += 1
    r.hset('stocksCode', 'lastUpdate', datetime.today())  # 加入当前获取的时间戳
    end = datetime.now() - start
    print(end)
    print('本次获取到%d条记录,当前已有%s条记录' % (count, r.hlen('stocksCode')))

start_spider()
