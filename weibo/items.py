# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # 原创微博数据
    id = scrapy.Field()  # 微博id
    bid = scrapy.Field()  # 微博bid
    user_id = scrapy.Field()
    screen_name = scrapy.Field()  # 用户昵称
    text = scrapy.Field()  # 微博正文
    location = scrapy.Field()  # 微博发布位置
    topics = scrapy.Field()  # 微博主题
    reposts_count = scrapy.Field()  # 转发数
    comments_count = scrapy.Field()  # 评论数
    attitudes_count = scrapy.Field()  # 点赞数
    created_at = scrapy.Field()  # 发布时间
    source = scrapy.Field()  # 发布来源

    # 转发微博数据
    retweet_id = scrapy.Field()
    retweet_bid = scrapy.Field()
    retweet_user_id = scrapy.Field()
    retweet_screen_name = scrapy.Field()
    retweet_text = scrapy.Field()
    retweet_location = scrapy.Field()
    retweet_topics = scrapy.Field()
    retweet_reposts_count = scrapy.Field()
    retweet_comments_count = scrapy.Field()
    retweet_attitudes_count = scrapy.Field()
    retweet_created_at = scrapy.Field()
    retweet_source = scrapy.Field()

class userItem(scrapy.Item):
    # 用户个人主页信息

    uid = scrapy.Field()
    name = scrapy.Field()  # 昵称
    province = scrapy.Field()
    gender = scrapy.Field()
    description = scrapy.Field()  # 简介
    sentiment = scrapy.Field()  # 感情状况
    authentication = scrapy.Field()  # 认证信息
    tweets_num = scrapy.Field()
    follows_num = scrapy.Field()
    fans_num = scrapy.Field()
