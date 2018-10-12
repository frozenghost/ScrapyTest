# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from functools import reduce


class ScrapytestPipeline(object):
    def process_item(self, item, spider):
        con = pymysql.connect(
            host='localhost',
            user='root',
            passwd='root',
            db='scrapy',
            charset='utf8',
            port=3306)
        cur = con.cursor()
        sql = "insert into product(image,price,deal,title,shop,location) values(%s)"
        lis = reduce(
            lambda x, y: ','.join([x, y]),
            map(lambda x: '\'' + x + '\'', [
                item['image'], item['price'], item['deal'], item['title'],
                item['shop'], item['location']
            ]))
        sql = sql % lis
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()

        return item


class FojobPipeline(object):
    def process_item(self, item, spider):
        con = pymysql.connect(
            host='localhost',
            user='root',
            passwd='root',
            db='scrapy',
            charset='utf8',
            port=3306)
        cur = con.cursor()
        keys = item.keys()
        columns = ','.join(keys)
        sql = "insert into job(%s) values(%s)"
        lis = ','.join(
            map(lambda x: '\'' + (item[x] if (item[x] != None) else '') + '\'',
                keys))
        sql = sql % (columns, lis)
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()

        return item