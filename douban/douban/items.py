# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    rating = scrapy.Field()
    rank = scrapy.Field()
    cover_url = scrapy.Field()
    is_playable = scrapy.Field()
    id = scrapy.Field()
    types = scrapy.Field()
    regions = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    release_date = scrapy.Field()
    actor_count = scrapy.Field()
    vote_count = scrapy.Field()
    score = scrapy.Field()
    actors = scrapy.Field()
    is_watched = scrapy.Field()
    category = scrapy.Field()

