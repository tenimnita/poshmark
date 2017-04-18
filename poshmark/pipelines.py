# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from poshmark import my_mongo


class DumpPipeline(object):
    def process_item(self, item, spider):
        my_mongo.item_collection.insert_one(dict(item))
        spider.logger.debug('saved')
        return item