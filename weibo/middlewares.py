# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from weibo import user_agents
import logging
import requests
import json
from weibo import settings
# from weibo import cookies

from weibo.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME
import pymongo

from collections import defaultdict
from scrapy.exceptions import NotConfigured

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


# 快代理
from w3lib.http import basic_auth_header
class ProxyMiddleware(object):
    # 代理服务器
    proxyServer = "http://tps121.kdlapi.com:15818"
    # 代理隧道验证信息
    proxyUser = "t19644257419076"
    proxyPass = "79phnk8e"
    proxyAuth = basic_auth_header(proxyUser, proxyPass)


    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxyServer
        request.headers["Proxy-Authorization"] = self.proxyAuth

    def process_response(self, request, response, spider):
        if response.status != 200:
            proxy = random.choice(self.proxyList).strip()
            # print("response ip info: " + proxy)
            # print("--------------------------------------")
            request.meta["proxy"] = proxy
            request.headers["Proxy-Authorization"] = self.proxyAuth

            return request
        return response

# import base64
# proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")


# ip 池
# class RandomProxyMiddleware(object):
#
#     def __init__(self, settings):
#         # 初始化配置和变量
#         # 在settings中写一个 PROXIES 列表配置
#         # 从settings中把代理读进来（把环境变量读进来）
#         self.proxies = settings.getlist("PROXIES")
#         self.stats = defaultdict(int)  # 默认值是0    统计次数
#         self.max_failed = 3  # 请求最多不超过3次
#
#     @classmethod
#     def from_cralwer(cls, crawler):
#         # 第一步 创建中间件对象
#         # 首先获取配置 HTTPPROXY_ENABLED 看看是否启用代理，
#         if not crawler.settings.getbool("HTTPPROXY_ENABLED"):  # 如果没有启用代理
#             raise NotConfigured
#         # auth_encoding = crawler.settings.get("HTTPPROXY_AUTH_ENCODING")  # 读取配置，这里暂时不用
#         # 第二步
#         return cls(crawler.settings)  # cls（）实际调用的是 init()函数，如果init接受参数，cls就需要参数
#
#     def process_request(self, request, spider):
#         # 为每个request对象随机分配一个ip代理
#         # 让这个请求使用代理, 初始url不使用代理ip
#         if self.proxies and not request.meta.get("proxy") and request.url not in spider.start_urls:
#             request.meta["proxy"] = random.choice(self.proxies)
#
#     def process_response(self, request, response, spider):
#         # 请求成功
#         cur_proxy = request.meta.get('proxy')
#         # 判断是否被对方禁封
#         if response.status > 400:
#             # 给相应的ip失败次数 +1
#             self.stats[cur_proxy] += 1
#             print("当前ip{}，第{}次出现错误状态码".format(cur_proxy, self.stats[cur_proxy]))
#         # 当某个ip的失败次数累计到一定数量
#         if self.stats[cur_proxy] >= self.max_failed:  # 当前ip失败超过3次
#             print("当前状态码是{}，代理{}可能被封了".format(response.status, cur_proxy))
#             # 可以认为该ip被对方封了，从代理池中删除这个ip
#             self.remove_proxy(cur_proxy)
#             del request.meta['proxy']
#             # 将这个请求重新给调度器，重新下载
#             return request
#
#         # 状态码正常的时候，正常返回
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # 第五步：请求失败
#         cur_proxy = request.meta.get('proxy')   # 取出当前代理
#         from twisted.internet.error import ConnectionRefusedError, TimeoutError
#         # 如果本次请求使用了代理，并且网络请求报错，认为这个ip出了问题
#         if cur_proxy and isinstance(exception, (ConnectionRefusedError, TimeoutError)):
#             print("当前的{}和当前的{}".format(exception, cur_proxy))
#             self.remove_proxy(cur_proxy)
#             del request.meta['proxy']
#             # 重新下载这个请求
#             return request
#
#     def remove_proxy(self, proxy):
#         if proxy in self.proxies:
#             self.proxies.remove(proxy)
#             print("从代理列表中删除{}".format(proxy))

# cookie池
class CookiesMiddleware(object):
    """
    每次请求都随机从账号池中选择一个账号去访问
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_request(self, request, spider):
        all_count = self.account_collection.find({'status': 'success'}).count()
        if all_count == 0:
            raise Exception('当前账号池为空')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'status': 'success'})[random_index]
        request.headers.setdefault('Cookie', random_account['cookie'])
        # logging.info(f'cookie: {temp}')
        # print("cookie info: " + random_account['cookie'])
        # # # print(random_account['cookie'])
        # print("--------------------------------------")
        request.meta['account'] = random_account


class RandomUserAgentMiddleware(object):
    """
    换User-Agent
    """
    def process_request(self, request, spider):
        temp = random.choice(user_agents.user_agent_list)
        request.headers['User-Agent'] = random.choice(user_agents.user_agent_list)
        # logging.info(f'User-Agent: {str(temp)}')
        # print("user-agent: " + str(temp))
        # print("--------------------------------------")


class WeiboSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeiboDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
