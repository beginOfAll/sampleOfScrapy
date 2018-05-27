# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import json
from functools import partial

dumps = partial(json.dumps, ensure_ascii=False)


class DoubanPipeline(object):
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='wjz', charset='utf8')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        sql = "INSERT INTO movie_douban(rating, rank, cover_url, is_playable, id, types, " \
              "regions, title, url, release_date, actor_count, vote_count, " \
              "score, actors, is_watched, category) " \
              "VALUES ('{0}', {1}, '{2}', {3}, '{4}', '{5}', " \
              "'{6}', '{7}', '{8}', '{9}', {10}, {11}, " \
              "'{12}', '{13}', {14}, '{15}')".format(
            item['rating'][0], item['rank'], item['cover_url'], str(item['is_playable']).upper(), item['id'], dumps(item['types']),
            dumps(item['regions']), item['title'], item['url'], item['release_date'], item['actor_count'], item['vote_count'],
            item['score'], dumps(item['actors']), str(item['is_watched']).upper(), item['category'])
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        return item

    def close_spider(self, spider):
        self.db.close()
