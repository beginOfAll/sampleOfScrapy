# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup, element
from ..items import ChengyuItem


class ChengyudaquanSpider(scrapy.Spider):
    name = 'chengyudaquan'
    allowed_domains = ['www.chengyudaquan.net']
    start_urls = ['http://www.chengyudaquan.net/feisizichengyu/list_{index}.html'.format(index=i) for i in range(1, 27)]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        spans = soup.find_all('span', class_='mainlia1 wzbtlist')
        self.logger.info('本页成语个数:' + str(len(spans)))
        for one in spans:
            for child in one.children:
                if child.name == 'a':
                    new_url = 'http://www.chengyudaquan.net' + child['href']
                    yield scrapy.Request(new_url, callback=self.single_parse)

    def single_parse(self, response):
        item = ChengyuItem()
        item['chengyu'] = ''
        item['pinyin'] = ''
        item['mean'] = ''
        item['source'] = ''
        item['english'] = ''
        item['common'] = ''
        item['isfour'] = False
        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = soup.find('h1', class_='wz-title')
        item['chengyu'] = h1.text
        if len(h1.text) == 4:
            item['isfour'] = True
        div = soup.find('div', class_='wz-picrr1')
        for i in div.children:
            if type(i) == element.NavigableString:
                if i.endswith('成语解释：'):
                    item['mean'] = str(i.next_sibling.next_sibling)
                elif i.endswith('成语出处：'):
                    item['source'] = str(i.next_sibling.next_sibling)
                elif i.endswith('常用程度：'):
                    item['common'] = str(i.next_sibling.next_sibling)
                elif i.endswith('英语翻译：'):
                    item['english'] = str(i.next_sibling.next_sibling)
        yield item
