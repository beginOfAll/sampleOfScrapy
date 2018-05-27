# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
import json
from ..items import DoubanItem


class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/chart']
    pattern = re.compile(r'&type=(\d+)&')
    interval_id = [
        '100:90',
        '90:80',
        '80:70',
        '70:60',
        '60:50',
        '50:40',
        '40:30',
        '30:20',
        '20:10',
        '10:0',
    ]
    xhr_url = \
        'https://movie.douban.com/j/chart/top_list?type={type}&interval_id={interval_id}&action=&start=0&limit=600'

    def parse(self, response):
        soup = BeautifulSoup(response.body.decode('utf-8'), 'html.parser')
        div = soup.find_all('div', class_='types')
        self.logger.info(len(div))
        for child in div[0].children:
            if child.name == 'span':
                a = child.a
                typenum = self.pattern.search(a['href']).group(1)
                for i in self.interval_id:
                    url = self.xhr_url.format(type=typenum, interval_id=i)
                    self.logger.info(a.text + '-' + i + ': ' + url)
                    yield scrapy.Request(url, meta={'category': a.text}, callback=self.parse_json)

    def parse_json(self, response):
        body = response.body.decode('utf-8')
        data = json.loads(body, encoding='utf-8')
        for one in data:
            item = DoubanItem()
            one['category'] = response.meta['category']
            # with open('movies.txt', 'a+', encoding='utf-8') as f:
            #    f.write(json.dumps(one, ensure_ascii=False))
            for (k, v) in one.items():
                item[k] = v
            yield item
