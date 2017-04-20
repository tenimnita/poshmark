# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PoshmarkItem(scrapy.Item):
    id = scrapy.Field()
    crawled_time = scrapy.Field()

    category_list = scrapy.Field()
    big_category = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()

    url = scrapy.Field()
    # img_urls = scrapy.Field()
    title = scrapy.Field()
    normalized_title = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    brand = scrapy.Field()
    like_count = scrapy.Field()
    comment_count = scrapy.Field()
    color = scrapy.Field()
    sale_date = scrapy.Field()
    condition = scrapy.Field()
    # category_link = scrapy.Field()
    crawled_date = scrapy.Field()
