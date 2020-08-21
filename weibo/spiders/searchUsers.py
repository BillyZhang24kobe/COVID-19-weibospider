# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from urllib.parse import unquote

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings

import weibo.utils.util as util
from weibo.items import userItem

import random

class SearchSpider(scrapy.Spider):
    name = 'search-user'
    allowed_domains = ['weibo.cn']
    settings = get_project_settings()
    rumor_user_ids = settings.getlist('ID_LIST')
    base_url = 'https://weibo.cn'

    def start_requests(self):
        for uid in self.rumor_user_ids:
            yield scrapy.Request(url="https://weibo.cn/{}/info".format(uid), callback=self.parse_information)


    def parse_information(self, response):
        """ 抓取个人信息 """
        information_item = userItem()
        uid = re.findall('(\d+)/info', response.url)[0]
        information_item['uid'] = re.findall('(\d+)/info', response.url)[0]

        # 获取标签里的所有text()
        information_text = ";".join(response.xpath('//div[@class="c"]//text()').extract())

        name = re.findall('昵称;?[：:]?(.*?);', information_text)
        information_item["name"] = 'none'
        if name and name[0]:
            information_item["name"] = name[0].replace(u"\xa0", "")
            # name = name[0].replace(u"\xa0", "")

        gender = re.findall('性别;?[：:]?(.*?);', information_text)
        information_item["gender"] = 'none'
        if gender and gender[0]:
            information_item["gender"] = gender[0].replace(u"\xa0", "")

        place = re.findall('地区;?[：:]?(.*?);', information_text)
        information_item["province"] = 'none'
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split()
            information_item["province"] = place[0]

        briefIntroduction = re.findall('简介;?[：:]?(.*?);', information_text)
        information_item["description"] = 'none'
        if briefIntroduction and briefIntroduction[0]:
            information_item["description"] = briefIntroduction[0].replace(u"\xa0", "")

        sentiment = re.findall('感情状况;?[：:]?(.*?);', information_text)
        information_item["sentiment"] = 'none'
        if sentiment and sentiment[0]:
            information_item["sentiment"] = sentiment[0].replace(u"\xa0", "")

        authentication = re.findall('认证信息;?[：:]?(.*?);', information_text)
        information_item["authentication"] = 'none'
        if authentication and authentication[0]:
            information_item["authentication"] = authentication[0].replace(u"\xa0", "")

        yield scrapy.Request(self.base_url + '/u/{}'.format(information_item['uid']),
                      callback=self.parse_further_information,
                      meta={'item': information_item},
                      dont_filter=True,
                      priority=1                      )

        # yield scrapy.Request(url=self.base_url + '/{}/profile?page=1'.format(uid),
        #               callback=self.parse_tweet,
        #               meta={'name': name, 'uid': uid},
        #               dont_filter=True,
        #               priority=1)

    def parse_further_information(self, response):

        information_item = response.meta.get('item')
        tweets_num = re.findall('微博\[(\d+)\]', response.text)
        if tweets_num:
            information_item['tweets_num'] = int(tweets_num[0])

        follows_num = re.findall('关注\[(\d+)\]', response.text)
        if follows_num:
            information_item['follows_num'] = int(follows_num[0])

        fans_num = re.findall('粉丝\[(\d+)\]', response.text)
        if fans_num:
            information_item['fans_num'] = int(fans_num[0])

        # print(information_item)
        # yield {'user': information_item, 'keyword': keyword}
        yield information_item

        # 获取用户微博  请求顺序priority(优先级)默认值是0,越大优先级越大,允许是负值
        # yield scrapy.Request(url=self.base_url + '/{}/profile?page=1'.format(information_item['uid']),
        #               callback=self.parse_tweet,
        #               meta={'nick_name': information_item['name'],
        #                     'keyword': 'tweetInfo'},
        #               dont_filter=True,
        #               priority=1)

        # # 获取关注列表
        # information_item['follows'] = []
        # yield scrapy.Request(url=self.base_url + '/{}/follow?page=1'.format(information_item['uid']),
        #               callback=self.parse_follow,
        #               meta={'item': information_item},
        #               dont_filter=True)  # keep searching the followers' list if next_level is set to True

    # 解析用户微博
    def parse_tweet(self, response):
        nick_name = response.meta.get('name')
        uid = response.meta.get('uid')
        if response.url.endswith('page=1'):
            # 如果是第1页，一次性获取后面的所有页
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield scrapy.Request(page_url, self.parse_tweet,
                                        meta={'name': nick_name, 'uid': uid},
                                        dont_filter=True)

        """
        解析本页的数据
        """
        tweet_nodes = response.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item = WeiboItem()

                tweet_item['nick_name'] = nick_name

                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href').extract()[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)

                # 微博URL
                tweet_item['weibo_url'] = 'https://weibo.cn/{}/{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))

                # 发表该微博用户id
                tweet_item['user_id'] = uid

                # 微博id
                tweet_item['id'] = '{}_{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))

                create_time_info = ''.join(tweet_node.xpath('.//span[@class="ct"]').xpath('string(.)').extract())
                tweet_item['source'] = 'none'
                if "来自" in create_time_info:
                    # 微博发表时间
                    # tweet_item['timestamp'] = create_time_info.split('来自')[0].strip()
                    # 发布微博的工具
                    tweet_item['source'] = create_time_info.split('来自')[1].strip()
                # else:
                tweet_item['timestamp'] = util.standardize_date(create_time_info.split('来自')[0])

                # # 转发数
                # repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()').extract()[0]
                # tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())

                # 原始微博，只有转发的微博才有这个字段
                repost_node = tweet_node.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    tweet_item['forwarded'] = '1'
                    tweet_item['forwarded_weibo'] = repost_node.extract()[0]
                else:
                    tweet_item['forwarded'] = '0'
                    tweet_item['forwarded_weibo'] = 'none'

                # 检测有没有阅读全文:
                all_content_link = tweet_node.xpath('.//a[text()="全文" and contains(@href,"ckAll=1")]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link.xpath('./@href').extract()[0]
                    yield scrapy.Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item})
                else:
                    # 微博内容
                    tweet_item['text'] = ''.join(tweet_node.xpath('./div[1]').xpath('string(.)').extract()
                                ).replace(u'\xa0', '').replace(u'\u3000', '').replace(' ', '').split('赞[', 1)[0]

                    # print(tweet_item)
                    # yield {'tweet': tweet_item, 'keyword': keyword}


                # 评论用户列表
                tweet_item['comment_list'] = []
                comment_url = self.base_url + '/comment/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
                yield scrapy.Request(url=comment_url, callback=self.parse_comment,
                                     meta={'item': tweet_item})

                # # 转发用户列表
                # tweet_item['repost_list'] = []
                # repost_url = self.base_url + '/repost/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
                # yield scrapy.Request(url=repost_url, callback=self.parse_repost,
                #                      meta={'item': tweet_item})
                #
                # # 点赞用户列表

            except Exception as e:
                self.logger.error(e)


    def parse_all_content(self, response):
        # 有阅读全文的情况，获取全文
        tweet_item = response.meta.get('item')
        tweet_item['text'] = ''.join(response.xpath('//*[@id="M_"]/div[1]').xpath('string(.)').extract()
                                        ).replace(u'\xa0', '').replace(u'\u3000', '').replace(' ', '').split('赞[', 1)[0]

        # yield tweet_item
        # print(tweet_item)

        # 评论用户列表
        tweet_item['comment_list'] = []
        comment_url = self.base_url + '/comment/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
        yield scrapy.Request(url=comment_url, callback=self.parse_comment,
                             meta={'item': tweet_item})
        # # 转发用户列表
        # tweet_item['repost_list'] = []
        # repost_url = self.base_url + '/repost/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
        # yield scrapy.Request(url=repost_url, callback=self.parse_repost,
        #                      meta={'item': tweet_item})


        # 点赞用户列表


    def parse_comment(self, response):
        # 获取评论者的id信息
        tweet_item = response.meta.get('item')
        # if response.url.endswith('page=1'):
        #     # 如果是第1页，一次性获取后面的所有页
        #     all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
        #     if all_page:
        #         all_page = all_page.group(1)
        #         all_page = int(all_page)
        #         for page_num in range(2, all_page + 1):
        #             page_url = response.url.replace('page=1', 'page={}'.format(page_num))
        #             yield scrapy.Request(page_url, self.parse_comment,
        #                                 meta={'item': tweet_item},
        #                                 dont_filter=True)

        comment_user_ids = tweet_item['comment_list']
        for comment_node in response.xpath('//div[@class="c" and contains(@id,"C_")]'):
            comment_user_ids.append(comment_node.xpath('./a[1]/@href').extract()[0].split('/u/', 1)[-1].split('/', 1)[-1])
            tweet_item['comment_list'] = comment_user_ids

            # yield tweet_item
        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield scrapy.Request(url, callback=self.parse_comment, meta={'item': tweet_item})

        # yield tweet_item
        # repost user ids
        tweet_item['repost_list'] = []
        repost_url = self.base_url + '/repost/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
        yield scrapy.Request(url=repost_url, callback=self.parse_repost,
                             meta={'item': tweet_item})

    def parse_repost(self, response):
        # 获取评论者的id信息
        tweet_item = response.meta.get('item')
        # if response.url.endswith('page=1'):
        #     # 如果是第1页，一次性获取后面的所有页
        #     all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
        #     if all_page:
        #         all_page = all_page.group(1)
        #         all_page = int(all_page)
        #         for page_num in range(2, all_page + 1):
        #             page_url = response.url.replace('page=1', 'page={}'.format(page_num))
        #             yield scrapy.Request(page_url, self.parse_repost,
        #                                 meta={'item': tweet_item},
                                        # dont_filter=True)

        repost_user_ids = tweet_item['repost_list']
        for repost_node in response.xpath('//div[@class="c"]'):
            id_str = repost_node.xpath('./a/@href').extract()
            if len(id_str) == 0: continue
            # print(id_str)
            if '?rand' in id_str[0]: continue
            if '/u/' in id_str[0]:
                repost_user_ids.append(id_str[0].split('/u/', 1)[-1].split('/', 1)[-1])
                # tweet_item['repost_list'] = repost_user_ids
            elif '/n/' in id_str[0]:
                repost_user_ids.append(id_str[0].split('/n/', 1)[-1].split('/', 1)[-1])
            else:
                repost_user_ids.append(id_str[0].split('/', 1)[1])
                # tweet_item['repost_list'] = repost_user_ids

            tweet_item['repost_list'] = repost_user_ids
            # yield tweet_item

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield scrapy.Request(url, callback=self.parse_repost, meta={'item': tweet_item})

        # yield tweet_item
        tweet_item['attitude_list'] = []
        attitude_url = self.base_url + '/attitude/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
        yield scrapy.Request(url=attitude_url, callback=self.parse_attitude,
                             meta={'item': tweet_item})


    def parse_attitude(self, response):
        tweet_item = response.meta.get('item')
        attitude_ids = tweet_item['attitude_list']
        for attitude_node in response.xpath('//div[@class="c"]'):
            id_str = attitude_node.xpath('./a/@href').extract()
            if len(id_str) == 0: continue
            # print(id_str)
            if '?rand' in id_str[0]: continue
            if '/u/' in id_str[0]:
                attitude_ids.append(id_str[0].split('/u/', 1)[-1].split('/', 1)[-1])
                # tweet_item['repost_list'] = repost_user_ids
            elif '/n/' in id_str[0]:
                attitude_ids.append(id_str[0].split('/n/', 1)[-1].split('/', 1)[-1])
            else:
                attitude_ids.append(id_str[0].split('/', 1)[1])
                # tweet_item['repost_list'] = repost_user_ids

            tweet_item['attitude_list'] = attitude_ids
            # yield tweet_item

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield scrapy.Request(url, callback=self.parse_attitude, meta={'item': tweet_item})


        yield tweet_item



    def parse_follow(self, response):
        """
        抓取关注列表
        """
        # urls = response.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        # nodes = re.findall('uid=(\d+)', ";".join(urls), re.S)
        # follows = [{'id': node} for node in nodes]

        node_l = response.xpath('//table//td[@valign][2]')
        information_item = response.meta['item']
        follows = information_item['follows']
        id = information_item['uid']
        for node in node_l:
            if node.xpath('./a[1]/text()').extract():
                url = node.xpath('.//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
                nodes_i = re.findall('uid=(\d+)', ";".join(url), re.S)
                nodes_n = node.xpath('./a[1]/text()').extract()[0]

                follows_date = {'name': nodes_n, 'id': nodes_i}
                follows.append(follows_date)

                # relationships_item = LevelOneRelationshipsItem()
                # relationships_item['id'] = id
                information_item['follows'] = follows
                # relationships_item['fans'] = []
                # yield {'user': information_item}

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield scrapy.Request(url, callback=self.parse_follow, meta={'item': information_item})

        yield information_item
