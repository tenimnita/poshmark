# -*- coding: utf-8 -*-
import json
import re
from functools import partial
from urlparse import urljoin, urlparse, parse_qs
import codecs
import scrapy
import datetime
from scrapy.http import Request

from poshmark import my_mongo
from poshmark.items import PoshmarkItem


class PoshmarkCategorySpider(scrapy.Spider):
    name = "poshmark_category"
    allowed_domains = ["poshmark.com"]

    start_urls = [
        'https://poshmark.com/category/Women',
        'https://poshmark.com/category/Men',
        'https://poshmark.com/category/Kids'
    ]

    def __init__(self, *args, **kwargs):
        super(PoshmarkCategorySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        print(u'parse big category: {}'.format(response.url))
        json_filter = response.xpath('//div[@data-react-class="Filters"]/@data-react-props').extract_first()
        json_filter = json.loads(json_filter, 'utf-8')
        categories = json_filter['filters']['categoriesSection']

        for big_category in categories:
            # print big_category
            for category in categories[big_category]['categories']:
                slug = categories[big_category]['categories'][category]['slug']
                url = u'{}-{}'.format(response.url, slug)
                yield scrapy.Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        print(u'parse category: {}'.format(response.url))
        json_filter = response.xpath('//div[@data-react-class="Filters"]/@data-react-props').extract_first()
        json_filter = json.loads(json_filter, 'utf-8')
        categories = json_filter['filters']['categoriesSection']

        for big_category in categories:
            # print big_category
            for category in categories[big_category]['categories']:
                sub_categories = categories[big_category]['categories'][category]['subCategories']
                for sub_category in categories[big_category]['categories'][category]['subCategories']:
                    slug = categories[big_category]['categories'][category]['subCategories'][sub_category]['slug']
                    url = u'{}-{}'.format(response.url, slug)
                    exist = my_mongo.category_collection.find_one(filter={
                        'url': url
                    })
                    if not exist:
                        my_mongo.category_collection.insert_one({
                            'url': url
                        })
