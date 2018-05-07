# http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002095&scale=60&ma=no&datalen=1023
# 获取深圳市场002095股票的60分钟数据，获取最近的1023个节点。
# Example:  http://hq.sinajs.cn/list=sh601006   即沪市601006
import json
import logging
import multiprocessing
from datetime import datetime
from multiprocessing.dummy import Pool
from urllib import request

import redis
from dateutil import rrule, parser

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


def get_datalen_bylastupdate(code, scale):
    """
    根据股票最后爬取时间,动态确定需要爬取的datalen
    :param code:
    :param scale:
    :return:
    """
    lastday = r.hget('lastUpdate', 'lastUpdate:%s' % code)  # 股票最后保存日期
    if lastday is None:
        return 1023
    now = datetime.now()
    offset = rrule.rrule(freq=rrule.DAILY, dtstart=parser.parse(lastday), until=now, byweekday=range(5)).count() - 1
    offset = offset * 240 / scale
    datalen = int(offset)
    return datalen


def get_stocks_html2json(code, scale):
    """
    获取股票代码的HTML页面
    :param code: 股票代码
    :param scale: 分时
    :param datalen: 长度
    :return: code股票代码，data数据，s当前分时
    """
    datalen = get_datalen_bylastupdate(code, scale)
    if datalen == 0:
        return code, 'null', str(scale)

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


def savedata(code, data, scale):
    """
    :param code: 股票代码
    :param data: 股票数据 {"high":99,"low":99}
    :param scale: 分时 5/30/60/240/1200
    :return:
    """
    datas = json.loads(data)  # list, list内存为每日数据
    r.hsetnx('lastUpdate', 'lastUpdate:%s' % code, datetime.now().strftime('%Y-%m-%d'))  # 该股最后保存时间,精确到日
    for i in datas:
        day = i.get('day')
        r.hset('stocks', 'stocks:%s:%s:%s' % (code, scale, day), json.dumps(i))  # stocks:sh600000:5:2018-05-04 10:10:00


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

    p.close()
    p.join()
    print('爬取' + str(len(datas)) + '条')
    print(datetime.now() - starttime)


start_spider()


def clear_data():
    r.delete('stocks')
    r.delete('teststocksCode')
    r.delete('stocksCode')
    r.delete('lastUpdate')
