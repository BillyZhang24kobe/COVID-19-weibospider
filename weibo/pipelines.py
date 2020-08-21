# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import csv
import os

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
# from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

# MongoDB
import pymongo
from pymongo.errors import DuplicateKeyError

from weibo.items import WeiboItem

import re
import time
import datetime

class CsvPipeline(object):
    def process_item(self, item, spider):
        base_dir = '结果文件' + os.sep + item['keyword']
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        file_path = base_dir + os.sep + item['keyword'] + '.csv'
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0
        if item:
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    header = [
                        'id', 'bid', 'user_id', '用户昵称', '微博正文',
                        '发布位置', '话题', '转发数', '评论数', '点赞数', '发布时间',
                        '发布工具', '转发id', '转发bid', '转发user_id', '转发_用户昵称',
                        '转发_微博正文', '转发_发布位置', '转发_话题', '转发_转发数',
                        '转发_评论数', '转发_点赞数', '转发_发布时间', '转发_发布工具'
                    ]
                    writer.writerow(header)
                writer.writerow(
                    [item['weibo'][key] for key in item['weibo'].keys()])
        return item

# items中加入时间戳
class TimePipeline():
    def process_item(self, item, spider):
        if isinstance(item, WeiboItem) :

            now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item['crawled_at'] = now
        return item

# 清洗时间
class WeiboSpiderPipeline():
    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date
        if re.match('\d{2}月\d{2}日', date):
            now_time = datetime.datetime.now()
            date = date.replace('月', '-').replace('日', '')
            date = str(now_time.year) + '-' + date
        if re.match('今天.*', date):
            date = re.match('今天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' ' + date


        return date


    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):

            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))

        return item


# class MongoPipeline(object):
#     def __init__(self, local_mongo_host, local_mongo_port, mongo_db):
#         self.local_mongo_host = local_mongo_host
#         self.local_mongo_port = local_mongo_port
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):
#
#         return cls(
#             local_mongo_host=crawler.settings.get('LOCAL_MONGO_HOST'),
#             local_mongo_port=crawler.settings.get('LOCAL_MONGO_PORT'),
#             mongo_db=crawler.settings.get('DB_NAME')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.local_mongo_host, self.local_mongo_port)
#         # 数据库名
#         self.db = self.client[self.mongo_db]
#         # 以Item中collection命名 的集合  添加index
#         self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)])
#
#     def close_spider(self, spider):
#         self.client.close()
#
#     def process_item(self, item, spider):
#         if isinstance(item, WeiboItem) :
#             self.db[item.collection].update({'id': item.get('id')},
#                                             {'$set': item},
#                                             True)
#         # elif isinstance(item, RelationshipsItem):
#         #     self.db[item.collection].update(
#         #         {'id': item.get('id')},
#         #         {'$addToSet':
#         #             {
#         #                 'follows': {'$each': item['follows']},
#         #                 'fans': {'$each': item['fans']}
#         #             }
#         #         },
#         #         True)
#         #
#         # elif isinstance(item, CommentItem):
#         #     self.insert_item(self.db[item.collection], item)
#
#         return item
#
#     @staticmethod
#     def insert_item(collection, item):
#         try:
#             collection.insert(dict(item))
#         except DuplicateKeyError:
#             """
#             说明有重复数据
#             """
#             pass


# class MyImagesPipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         if len(item['weibo']['pics']) == 1:
#             yield scrapy.Request(item['weibo']['pics'][0],
#                                  meta={
#                                      'item': item,
#                                      'sign': ''
#                                  })
#         else:
#             sign = 0
#             for image_url in item['weibo']['pics']:
#                 yield scrapy.Request(image_url,
#                                      meta={
#                                          'item': item,
#                                          'sign': '-' + str(sign)
#                                      })
#                 sign += 1
#
#     def file_path(self, request, response=None, info=None):
#         image_url = request.url
#         item = request.meta['item']
#         sign = request.meta['sign']
#         base_dir = '结果文件' + os.sep + item['keyword'] + os.sep + 'images'
#         if not os.path.isdir(base_dir):
#             os.makedirs(base_dir)
#         image_suffix = image_url[image_url.rfind('.'):]
#         file_path = base_dir + os.sep + item['weibo'][
#             'id'] + sign + image_suffix
#         return file_path
#
#
# class MyVideoPipeline(FilesPipeline):
#     def get_media_requests(self, item, info):
#         if item['weibo']['video_url']:
#             yield scrapy.Request(item['weibo']['video_url'],
#                                  meta={'item': item})
#
#     def file_path(self, request, response=None, info=None):
#         item = request.meta['item']
#         base_dir = '结果文件' + os.sep + item['keyword'] + os.sep + 'videos'
#         if not os.path.isdir(base_dir):
#             os.makedirs(base_dir)
#         file_path = base_dir + os.sep + item['weibo']['id'] + '.mp4'
#         return file_path


class MongoPipeline(object):
    def open_spider(self, spider):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(settings.get('MONGO_URI'))
            self.db = self.client['weibo']
            self.collection = self.db['user7']
        except ModuleNotFoundError:
            spider.pymongo_error = True

    def process_item(self, item, spider):
        try:
            import pymongo

            new_item = copy.deepcopy(item)
            # if not self.collection.find_one({'id': new_item['weibo']['id']}):
            if not self.collection.find_one({'id': new_item['uid']}):
                # self.collection.insert_one(dict(new_item['weibo']))
                self.collection.insert_one(dict(new_item))
            else:
                # self.collection.update_one({'id': new_item['weibo']['id']},
                #                            {'$set': dict(new_item['weibo'])})
                self.collection.update_one({'id': new_item['uid']},
                                           {'$set': dict(new_item)})
        except pymongo.errors.ServerSelectionTimeoutError:
            spider.mongo_error = True

    def close_spider(self, spider):
        try:
            self.client.close()
        except AttributeError:
            pass


# class MysqlPipeline(object):
#     def create_database(self, mysql_config):
#         """创建MySQL数据库"""
#         import pymysql
#         sql = """CREATE DATABASE IF NOT EXISTS %s DEFAULT
#             CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""" % settings.get(
#             'MYSQL_DATABASE', 'weibo')
#         db = pymysql.connect(**mysql_config)
#         cursor = db.cursor()
#         cursor.execute(sql)
#         db.close()
#
#     def create_table(self):
#         """创建MySQL表"""
#         sql = """
#                 CREATE TABLE IF NOT EXISTS weibo (
#                 id varchar(20) NOT NULL,
#                 bid varchar(12) NOT NULL,
#                 user_id varchar(20),
#                 screen_name varchar(30),
#                 text varchar(2000),
#                 article_url varchar(100),
#                 topics varchar(200),
#                 at_users varchar(1000),
#                 pics varchar(3000),
#                 video_url varchar(1000),
#                 location varchar(100),
#                 created_at DATETIME,
#                 source varchar(30),
#                 attitudes_count INT,
#                 comments_count INT,
#                 reposts_count INT,
#                 retweet_id varchar(20),
#                 PRIMARY KEY (id)
#                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
#         self.cursor.execute(sql)
#
#     def open_spider(self, spider):
#         try:
#             import pymysql
#             mysql_config = {
#                 'host': settings.get('MYSQL_HOST', 'localhost'),
#                 'port': settings.get('MYSQL_PORT', 3306),
#                 'user': settings.get('MYSQL_USER', 'root'),
#                 'password': settings.get('MYSQL_PASSWORD', '123456'),
#                 'charset': 'utf8mb4'
#             }
#             self.create_database(mysql_config)
#             mysql_config['db'] = settings.get('MYSQL_DATABASE', 'weibo')
#             self.db = pymysql.connect(**mysql_config)
#             self.cursor = self.db.cursor()
#             self.create_table()
#         except ImportError:
#             spider.pymysql_error = True
#         except pymysql.OperationalError:
#             spider.mysql_error = True
#
#     def process_item(self, item, spider):
#         data = dict(item['weibo'])
#         data['pics'] = ','.join(data['pics'])
#         keys = ', '.join(data.keys())
#         values = ', '.join(['%s'] * len(data))
#         sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
#                      DUPLICATE KEY UPDATE""".format(table='weibo',
#                                                     keys=keys,
#                                                     values=values)
#         update = ','.join([" {key} = {key}".format(key=key) for key in data])
#         sql += update
#         try:
#             self.cursor.execute(sql, tuple(data.values()))
#             self.db.commit()
#         except Exception:
#             self.db.rollback()
#         return item
#
#     def close_spider(self, spider):
#         try:
#             self.db.close()
#         except Exception:
#             pass


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['weibo']['id'] in self.ids_seen:
            raise DropItem("过滤重复微博: %s" % item)
        else:
            self.ids_seen.add(item['weibo']['id'])
            return item
