# -*- coding: utf-8 -*-

BOT_NAME = 'weibo'
SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'
LOG_LEVEL = 'ERROR'

# import datetime
# LOG_LEVEL = 'DEBUG'
# startDate = datetime.datetime.now().strftime('%Y%m%d')
# LOG_FILE = f"ClawerSlaver_1_log{startDate}.txt"	# 将log写入文件中


ROBOTSTXT_OBEY = False

# speed up the downloading speed
DOWNLOAD_DELAY = 0.15  # 访问完一个页面再访问下一个时需要等待的时间
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 100
CONCURRENT_REQUESTS_PER_IP = 100
# COOKIES_ENABLED = False

# ip 池
# HTTPPROXY_ENABLED = True
# PROXIES = []

DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'weibo.middlewares.CookiesMiddleware': 554,
    'weibo.middlewares.ProxyMiddleware': 555,
    'weibo.middlewares.RandomUserAgentMiddleware': 556,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}


ITEM_PIPELINES = {
    # 'weibo.pipelines.CsvPipeline': 300,
    'weibo.pipelines.TimePipeline': 300,
    'weibo.pipelines.WeiboSpiderPipeline': 301,
    'weibo.pipelines.MongoPipeline': 302,
}

RETRY_HTTP_CODES = [401, 403, 408, 414, 418, 500, 502, 503, 504]

# MongoDb 配置
LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'weibo'

import json
with open("./userID_7.json", 'r') as jfile:
   list = json.load(jfile)
ID_LIST = list

# 要搜索的关键词列表，可写多个
KEYWORD_LIST = ['肺炎', 'Sars', '新冠', '冠状', 'COVID-19']
# 要搜索的微博类型，0代表搜索全部微博，1代表搜索全部原创微博，2代表热门微博，3代表关注人微博，4代表认证用户微博，5代表媒体微博，6代表观点微博
WEIBO_TYPE = 0
# 筛选结果微博中必需包含的内容，0代表不筛选，获取全部微博，1代表搜索包含图片的微博，2代表包含视频的微博，3代表包含音乐的微博，4代表包含短链接的微博
CONTAIN_TYPE = 0
# 筛选微博的发布地区，精确到省或直辖市，值不应包含“省”或“市”等字，如想筛选北京市的微博请用“北京”而不是“北京市”，想要筛选安徽省的微博请用“安徽”而不是“安徽省”，可以写多个地区，
# 具体支持的地名见region.py文件，注意只支持省或直辖市的名字，省下面的市名及直辖市下面的区县名不支持，不筛选请用”全部“
REGION = ['全部']
# 搜索的起始日期，为yyyy-mm-dd形式，搜索结果包含该日期
START_DATE = '2019-12-01'
# 搜索的终止日期，为yyyy-mm-dd形式，搜索结果包含该日期
END_DATE = '2019-12-31'
