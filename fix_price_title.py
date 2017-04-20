from poshmark import my_mongo
from poshmark.spiders.poshmark_spider import PoshmarkSpider

if __name__ == '__main__':
    skip = 0
    limit = 1000
    items = []
    n_row = 1
    spider = PoshmarkSpider()

    while True:
        print 'start new', skip, limit
        items = my_mongo.item_collection.find(filter={
            # 'id': '58ecf0e178b31c3528068b17'
        }, projection={
            'title': 1,
            'price': 1,
            'id': 1
        }).skip(skip).limit(limit)
        has_item = False
        #############################################
        for item in items:
            if item['price']:
                item['price'] = item['price'].strip()
            if item['title']:
                item['normalized_title'] = spider.normalize_title(item['title'])
            my_mongo.item_collection.update_one(filter={
                'id': item['id']
            }, update={
                '$set': {
                    'price': item['price'],
                    'normalized_title': item['normalized_title']
                }
            })
            has_item = True
            # print u'updated {}'.format(item['id'])
        if has_item == False:
            break
        skip += limit
