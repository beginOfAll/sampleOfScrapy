# -*- coding: utf-8 -*-
import scrapy


class BaidulistSpider(scrapy.Spider):
    name = 'baidulist'
    allowed_domains = ['www.baidu.com']
    start_urls = ['https://www.baidu.com/s?wd=%E5%BF%AB%E9%80%92%2B%E5%91%83%E6%94%B6%E4%BB%B6%E4%BA%BA']

    def parse(self, response):
        print(response.text)
