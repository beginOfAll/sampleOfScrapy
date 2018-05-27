# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ChengyuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    chengyu = scrapy.Field()
    pinyin = scrapy.Field()
    mean = scrapy.Field()
    source = scrapy.Field()
    english = scrapy.Field()
    common = scrapy.Field()
    isfour = scrapy.Field()
