import json
import multiprocessing
import re
from multiprocessing.dummy import Pool
from urllib import request

import itertools

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
        d = {'code': code, 'name': name}
        stocks.append(d)
    if not stocks:
        raise IndexError
    return stocks


def combine_symbol():
    """
    合并处理后的多个dict
    :return: dict [{'sh600000':'A'},{'sh600001','B'},...]
    """
    symbols_list = []
    g = get_stocks_symbol()
    for n in g:
        symbols_list += n
    return symbols_list


def savedata2json(data):
    """
    存储为txt，以,分割
    :return:
    """
    with open('stocksCode.json', 'w') as js:
        json.dump(data, js)
    print('***写入文件完毕***')


def start_spider():
    p = Pool(multiprocessing.cpu_count())
    print('***爬取所有股票代码中...***')
    stocks = []
    data = []
    for page in range(1, 36):
        l = p.apply_async(get_stocks_symbol, args=(page,))
        stocks.append(l)
    for stock in stocks:
        data.extend(stock.get())
    print('共获取到%d条记录' % len(data))
    savedata2json(data)
    print(data)

start_spider()
