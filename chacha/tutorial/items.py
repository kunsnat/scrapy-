# -*- coding: utf-8 -*-

import scrapy


class ChaXunItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    progress = scrapy.Field()
    type = scrapy.Field()  # sup_item  announce

    index = scrapy.Field()

    url = scrapy.Field()

    area = scrapy.Field()
    updateTime = scrapy.Field()

    money = scrapy.Field()
    validTime = scrapy.Field()

    industry = scrapy.Field()

    content = scrapy.Field()

    policyType = scrapy.Field()

    number = scrapy.Field() # 文号

    system = scrapy.Field() # 发文体系

    notetype = scrapy.Field() # 公示类型

    policyTrail = scrapy.Field() # 政策轨迹

    dataSource = scrapy.Field() # 数据来源

    fromUrl = scrapy.Field() # 记录目标item来自的查询url, 便于分别保存excel数据.

class CheckItem(scrapy.Item):

    test = scrapy.Field()


class CityItem(scrapy.Item):
    name = scrapy.Field()  # data-name
    title = scrapy.Field()  # title
    level = scrapy.Field() # data-level
    id = scrapy.Field() # data-id
    text = scrapy.Field() # //a/text()
    url = scrapy.Field() # tmp url
