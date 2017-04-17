# -*- coding: utf-8 -*-

import re
from functools import partial
from urlparse import urljoin, urlparse, parse_qs
import codecs
import scrapy
import datetime
from scrapy.http import Request

from poshmark import my_mongo
from poshmark.items import PoshmarkItem


class PoshmarkSpider(scrapy.Spider):
    name = "poshmark"
    allowed_domains = ["poshmark.com"]

    start_urls = [
        # 'https://poshmark.com/category/Women-Accessories-Belts',
        # 'https://poshmark.com/category/Men',
    ]

    # cookies = {
    #     'ui': '%7B%22dh%22%3A%22tenimnita%22%2C%22uit%22%3A%22https%3A%2F%2Fdtpmhvbsmffsz.cloudfront.net%2Fusers%2F2017%2F03%2F13%2F58c79031649d0cbac1020553%2Ft_58c79031649d0cbac102055d.jpg%22%2C%22uid%22%3A%2258c79031649d0cbac1020553%22%2C%22em%22%3A%22tenimnita%40gmail.com%22%2C%22fn%22%3A%22Ten+Imnita%22%2C%22roles%22%3A%5B%5D%2C%22ge%22%3A%22male%22%7D',
    #     '_web_session': 'BAh7CEkiD3Nlc3Npb25faWQGOgZFRkkiJTVjMmVjZmYzODg5NTIwMTBmMjI4OTBhNGM5NjlhMGI5BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMVhEZ0ZHNGdjU01RYUIwQW1XNkgvQ2ZSN3Q2WGliTnBqaVhGYXZDMkVaTlk9BjsARkkiEWFjY2Vzc190b2tlbgY7AEZJIgGWTlRoak56a3dNekUyTkRsa01HTmlZV014TURJd05UVXpmREUxTWpNM05qSTVPRFI4TUM0eWZEQjhOVGhtTVRrellUZzBOMkl5WmpNek5EaGhNbVppWm1VNWZEQjhaa0k0ZFMwMmFVVjJibk5MV2xaVlprdzRkelU0TkVKUmRXYzNPWGd5TldSeWNUUnJhRVJ2ZGpOMU5BBjsARg%3D%3D--32b0324fc6727297f8c3229920b3cd28cb080a76',
    # }

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield scrapy.Request(url=url, headers=self.headers)

    def __init__(self, *args, **kwargs):
        super(PoshmarkSpider, self).__init__(*args, **kwargs)
        # for i, url in enumerate(self.start_urls):
        #     self.start_urls[i] = url + '?availability=sold_out'

        for category_url in my_mongo.category_collection.find():
            self.start_urls.append(category_url['url'] + '?availability=sold_out')

    def parse_item(self, item, response):
        self.logger.info('parse item: {}'.format(response.url))
        # item = PoshmarkItem()
        item['id'] = self.parse_id(response.url)
        if not item['id']:
            return
        exist = my_mongo.item_collection.find_one(filter={
            'id': item['id']
        })
        if exist:
            print 'existed'
            return
        item['url'] = response.url
        item['crawled_time'] = datetime.datetime.now()
        # item['bread_crumb'] = response.xpath('//li[@itemscope="itemscope"]/a/span/text()').extract()
        item['title'] = response.xpath('//h1[@class="title"]/text()').extract_first()
        item['price'] = response.xpath('//div[@class="price"]/text()').extract_first()
        # item['img_urls'] = response.xpath('//div[@class="carousel-inner"]//img/@src').extract()
        item['category_list'] = self.parse_category(response)
        if len(item['category_list']) > 0:
            item['big_category'] = item['category_list'][0]
        if len(item['category_list']) > 1:
            item['category'] = item['category_list'][1]
        if len(item['category_list']) > 2:
            item['sub_category'] = item['category_list'][2]
        item['color'] = response.xpath('//a[@data-pa-name="listing_details_color"]/text()').extract()
        item['sale_date'] = response.xpath('//span[@class="time"]/text()').extract_first()
        item['crawled_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        yield item

    def parse_id(self, url):
        obj = re.match(r'(.*)[-/]([a-z0-9]+)', url)
        if obj:
            return obj.group(2)
        return None

    def parse_category(self, response):
        for tag_list in response.xpath('//div[@class="tag-con"]'):
            cate_name = tag_list.xpath('./div[@class="secondary-title"]/text()').extract_first()
            if re.match(r'category', cate_name, re.IGNORECASE):
                categories = tag_list.xpath('.//a/text()').extract()
                return categories
        return None

    def parse(self, response):
        self.logger.info('parse list: {}'.format(response.url))
        # check no_result
        no_result = response.xpath('//div[@class="no-listings-search"]').extract_first()
        if no_result is not None:
            self.logger.info('no more result for: {}'.format(response.url))
            return
        # go item's pages
        url_items = response.xpath('//div[@id="tiles-con"]/div')
        if len(url_items) == 0:
            self.logger.warning('Cannot extract URL from: {}'.format(response.url))
        for url_item in url_items:
            url = url_item.xpath('.//div[@class="item-details"]//a/@href').extract_first()
            if not url:
                continue
            obj = re.match(r'(.*)/listing/', url)
            if obj:
                url = urljoin(response.url, url)
                like_count = url_item.xpath('.//span[@class="count has-likes"]/text()').extract_first()
                comment_count = url_item.xpath('.//span[@class="count"]/text()').extract_first()
                size = url_item.xpath('.//span[@class="val"]/text()').extract_first()
                brand = url_item.xpath('.//li[@class="brand"]/a/text()').extract_first()
                condition = url_item.xpath('.//a[contains(@class, "condition")]/text()').extract_first()
                # print url, like_count, comment_count
                # print size
                # print brand
                id = self.parse_id(url)
                exist = my_mongo.item_collection.find_one(filter={
                    'id': id
                })
                if not exist:
                    # print url
                    yield Request(url=url, callback=partial(self.parse_item, PoshmarkItem(
                        # category_link=response.url,
                        like_count=like_count,
                        comment_count=comment_count,
                        size=size,
                        brand=brand,
                        condition=condition
                    )))
        # go next page
        obj = re.match(r'(.*)&max_id=(\d+)', response.url)
        if obj:
            next_page = obj.group(1) + '&max_id={}'.format(int(obj.group(2)) + 1)
            yield Request(url=next_page, callback=self.parse)
        else:
            tmp = re.match(r'(.*)availability=sold_out', response.url)
            if tmp:
                next_page = tmp.group(1) + 'availability=sold_out&max_id=2'
                yield Request(url=next_page, callback=self.parse)
            else:
                self.logger.info(u'not match paging site {}'.format(response.url))
