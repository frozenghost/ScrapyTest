# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class ProductItem(Item):

    collection = 'products'

    image = Field()
    price = Field()
    deal = Field()
    title = Field()
    shop = Field()
    location = Field()


class JobItem(Item):

    collection = 'jobs'

    name = Field()
    company = Field()
    area = Field()
    salary = Field()
    publishdate = Field()
    link = Field()
    source = Field()
    downloaddate = Field()
