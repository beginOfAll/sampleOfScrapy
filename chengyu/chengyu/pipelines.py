# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class ChengyuPipeline(object):
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='wjz', charset='utf8')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        sql = "INSERT INTO chengyu (chengyu, mean, source, english, common, isfour) " \
              "VALUES ('{0}', '{1}', '{2}', '{3}', {4}, {5})".format(item['chengyu'],
                                                                     item['mean'],
                                                                     item['source'],
                                                                     item['english'],
                                                                     1 if item['common'] == '常用成语' else 0,
                                                                     1 if item['isfour'] else 0)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        return item

    def close_spider(self, spider):
        self.db.close()
