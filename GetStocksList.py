import re
from urllib import request

all_stocks_symbol_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/' \
                        'Market_Center.getHQNodeData?page=%s&num=100&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=init'


def get_stocks_symbol():
    """
    获取股票代码
    :return List
    """
    print('***爬取所有股票代码中...***')
    n = 1
    while True:
        html = request.urlopen(all_stocks_symbol_url % n).read().decode('gbk')
        symbols = re.findall('symbol:\"(.*?)\"', html)
        if html == 'null':
            print('***爬取完毕，等待写入***')
            break
        print('***正在爬取第 %s 页***' % n)
        n += 1
        yield symbols


def combine_symbol():
    """
    合并处理后的多个list为一个list
    :return: List [sh600000,sh600001...]
    """
    symbols_list = []
    g = get_stocks_symbol()
    for n in g:
        symbols_list += n
    return symbols_list


def symbols2txt():
    """
    存储为txt，以,分割
    :return:
    """
    symbols_list = combine_symbol()
    with open('stocks_code.txt', 'w') as f:
        f.write(','.join(map(str, symbols_list)))
    print('***写入完毕***')


symbols2txt()
