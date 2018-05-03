# http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002095&scale=60&ma=no&datalen=1023
# 获取深圳市场002095股票的60分钟数据，获取最近的1023个节点。
# Example:  http://hq.sinajs.cn/list=sh601006   即沪市601006
import json
import logging
import multiprocessing
import os
from datetime import datetime
from multiprocessing.dummy import Pool
from urllib import request

import redis

import DataSource

logging.basicConfig(level=logging.INFO)

url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?' \
      'symbol=%s&scale=%s&ma=qianfuquan&datalen=%s'

r = redis.Redis(connection_pool=DataSource.DATASOURCE_POOL)


def load_stocks_code(hashname):
    """
    载入股票列表，每只股票以','分割
    :return: list
    """
    stocks_codes = r.hkeys(hashname)
    return stocks_codes


def get_stocks_html2json(code, scale, datalen='5'):
    """
    获取股票代码的HTML页面
    :param code: 股票代码
    :param scale: 分时
    :param datalen: 长度
    :return: code股票代码，data数据，s当前分时
    """
    htmlurl = url % (code, scale, datalen)
    try:
        html = request.urlopen(htmlurl).read().decode('gbk')
        if html == 'null':
            return code, 'null', str(scale)
        # 解析通过html获得股票数据，使之成为规范化json数据
        data = html.replace('day', '\"day\"').replace('open', '\"open\"').replace('high', '\"high\"') \
            .replace('low', '\"low\"').replace('close', '\"close\"').replace('volume', '\"volume\"')
        return code, data, str(scale)
    except Exception as e:
        print('连接失败:' + htmlurl, e)
        return code, 'null', str(scale)


def combine_li_delete_duplicate(li1, li2):
    """
    去除[{a:b},{a:b},{a:c}]的重复dict元素
    :param li1:
    :return:
    """
    print(li1)
    for i in li2:
        print(type(i))
    print(type(li1))
    temp_list = list(set([str(i) for i in li1]))
    li = [eval(i) for i in temp_list]
    return li


def savedata(code, data, scale):
    """
    :param code: 股票代码
    :param data: 股票数据 {"high":99,"low":99}
    :param scale: 分时 5/30/60/240/1200
    :return:
    """
    if r.hexists('stocks-%s' % scale, 'stocks:%s:%s' % (code, scale)):
        old_data = eval(json.loads(r.hget('stocks-%s' % scale, 'stocks:%s:%s' % (code, scale))))  # 如果存在原值,读取原值
        new_data = eval(data)
        print('test')
        data = combine_li_delete_duplicate(old_data, new_data)
    print('test')
    r.hset('stocks-%s' % scale, 'stocks:%s:%s' % (code, scale), json.dumps(data))


def start_spider():
    stocks_code = load_stocks_code('teststocksCode')
    scales = [5, 30]
    p = Pool(multiprocessing.cpu_count())
    starttime = datetime.now()
    datas = []
    for code in stocks_code:
        print('获取' + code)
        for s in scales:
            data = p.apply_async(get_stocks_html2json, args=(code, s,))
            # data.get()方法是阻塞的，如果放在循环里，会阻塞进程的运行
            datas.append(data)
    print('解析数据中...')
    for data in datas:
        if data.get()[1] != 'null':
            p.apply_async(savedata, args=(data.get()[0], data.get()[1], data.get()[2],))
        else:
            print('该项不存在:代码%s;分时%s' % (data.get()[0], data.get()[2]))

    p.close()
    p.join()
    print('爬取' + str(len(datas)) + '条')
    print(datetime.now() - starttime)


start_spider()
