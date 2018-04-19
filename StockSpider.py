from bs4 import BeautifulSoup

# http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=100&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=init

# http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002095&scale=60&ma=no&datalen=1023
# 获取深圳市场002095股票的60分钟数据，获取最近的1023个节点。
# Example:  http://hq.sinajs.cn/list=sh601006   即沪市601006
url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData' \
      '?symbol=%s&scale=%s&ma=qianfuquan&datalen=%s'


# 获取JSON数据
def get_stocksHTML(fenshi, datalen, single=False, ):
    if single is True:
        # 单个获取,为全字符,如sh600001,sz000001
        return url % fenshi, single
    # 批量获取
    pass


def parse_stockdata(html):
    pass


def download2Json():
    pass
