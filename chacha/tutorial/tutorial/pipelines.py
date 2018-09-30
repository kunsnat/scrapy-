# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import scrapy
import os
from openpyxl import Workbook
from scrapy.pipelines.files import FilesPipeline
import urlparse
from os.path import basename,dirname,join
import urllib

class TutorialPipeline(FilesPipeline):


    # def get_media_requests(self, item,info):
    #     for url in item["file_urls"]:
    #         yield scrapy.Request(url)

    # def file_path(self, request, response=None, info=None):
    #     path = ""
    #     # return join(basename(dirname(path)),basename(path))
    #
    #     return "D://"

    # def file_path(self, request, response=None, info=None):
    #     path = os.path.join('D:\\result', ''.join( [request.url.replace('//', '_').replace('/', '_').replace(':', '_').replace('.', '_').replace('__','_'), '.zip']))
    #     return path


    def parseT(self, value):
                return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):
        test = [item['title'], item['progress'], item['type'], item['area'], item['updateTime'], item['money'], item['validTime'],
                item['industry'], item['policyType'], '' ]
        spider.ws.append(test)
        spider.wb.save('chacha.xlsx')

        return item



