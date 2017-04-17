import pymongo
from pymongo.mongo_client import MongoClient

client = MongoClient('localhost', 27017)  # default maxPoolSize = 100
db = client['poshmark']
#
item_collection = db['item']
item_collection.create_index([
    ('id', pymongo.ASCENDING),
], unique=True)
item_collection.create_index([
    ('crawled_date', pymongo.ASCENDING),
], unique=False)


category_collection = db['category']
category_collection.create_index([
    ('url', pymongo.ASCENDING),
], unique=True)