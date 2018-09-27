# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    progress = scrapy.Field()
    type = scrapy.Field()  # sup_item  announce
    url = scrapy.Field()

    area = scrapy.Field()
    updateTime = scrapy.Field()

    money = scrapy.Field()
    validTime = scrapy.Field()

    industry = scrapy.Field()

    content = scrapy.Field()

    policyType = scrapy.Field()

    file_urls = scrapy.Field()
    files = scrapy.Field()
