# http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002095&scale=60&ma=no&datalen=1023
# 获取深圳市场002095股票的60分钟数据，获取最近的1023个节点。
# Example:  http://hq.sinajs.cn/list=sh601006   即沪市601006
import json
import os
from multiprocessing.dummy import Pool
from urllib import request

import logging

from datetime import datetime

import multiprocessing
from urllib.error import URLError

logging.basicConfig(level=logging.INFO)

url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?' \
      'symbol=%s&scale=%s&ma=qianfuquan&datalen=%s'


def load_stocks_code(filename):
    """
    载入股票列表，每只股票以','分割
    :param filename: 文件路径
    :return: list
    """
    with open(filename, 'r') as f:
        stocks_codes = json.load(f)
    return stocks_codes


def get_stocks_html2json(stocks_codename, scale, datalen='1023'):
    """
    获取股票代码的HTML页面
    :param stocks_codename: 股票代码和名称
    :param scale: 分时
    :param datalen: 长度
    :return: code股票代码，data数据，s当前分时
    """
    htmlurl = url % (stocks_codename['code'], scale, datalen)
    try:
        html = request.urlopen(htmlurl).read().decode('gbk')
        if html == 'null':
            return stocks_codename, 'null', str(scale)
        # 解析通过html获得股票数据，使之成为规范化json数据
        data = html.replace('day', '\"day\"').replace('open', '\"open\"').replace('high', '\"high\"') \
            .replace('low', '\"low\"').replace('close', '\"close\"').replace('volume', '\"volume\"')
        return stocks_codename, data, str(scale)
    except Exception as e:
        print('连接失败:' + htmlurl, e)
        return stocks_codename, 'null', str(scale)


def createfolder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def savadata2json(stock, data, scale):
    """
    保存为JSON数据，并构造JSON结构
    :param stock: 股票代码和名称
    :param data: 股票数据
    :param scale: 分时
    :return:
    """
    folderpath = 'stocks/' + scale
    createfolder(folderpath)
    result = {'code': stock['code'], 'name': stock['name'], 'data': data}
    with open(folderpath + '/' + stock['code'] + '.json', 'w') as js:
        json.dump(result, js)


def start_spider():
    stocks_codename = load_stocks_code('StocksCode.json')
    scales = [240]
    p = Pool(multiprocessing.cpu_count())
    starttime = datetime.now()
    datas = []
    for stock in stocks_codename:
        print('获取' + stock['code'])
        for s in scales:
            data = p.apply_async(get_stocks_html2json, args=(stock, s,))
            # data.get()方法是阻塞的，如果放在循环里，会阻塞进程的运行
            datas.append(data)
    print('解析数据中...')
    for data in datas:
        if data.get()[1] != 'null':
            print(data.get()[0])
            p.apply_async(savadata2json, args=(data.get()[0], data.get()[1], data.get()[2],))
        else:
            print('该项不存在:代码%s;分时%s' % (data.get()[0], data.get()[2]))

    p.close()
    p.join()
    print('爬取' + str(len(datas)) + '条')
    print(datetime.now() - starttime)

start_spider()
