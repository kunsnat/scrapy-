# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline
import json
import scrapy
import os
import urlparse

class TutorialPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None):
        parse_result = urlparse(request.url)
        path = parse_result.path
        basename = os.path.basename(path)
        return basename


    def get_media_requests(self, item,info):
        print 'this is form get mdediso aaaa'
        for url in item["file_urls"]:
            yield scrapy.Request(url)


    def parseT(self, value):
                return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):
        test = [item['title'], item['progress'], item['type'], item['area'], item['updateTime'], item['money'], item['validTime'],
                item['industry'], item['policyType'], '' ]
        spider.ws.append(test)
        spider.wb.save('chacha.xlsx')

        return item



