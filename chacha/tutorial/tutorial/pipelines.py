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

class TutorialPipeline(object):

    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['标题', '进度', '类型', '适用地区', '发文时间', '扶持金额', '有效期限', '适用行业', '政策分类', '申报详情', '附件列表'])  # 设置表头

    # def get_media_requests(self, item,info):
    #     for url in item["file_urls"]:
    #         yield scrapy.Request(url)

    # def file_path(self, request, response=None, info=None):
    #     path = ""
    #     # return join(basename(dirname(path)),basename(path))
    #
    #     return "D://"

    def parseT(self, value):
            return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):
        test = [item['title'], item['progress'], item['type'], item['area'], item['updateTime'], item['money'], item['validTime'],
                item['industry'], item['policyType'], item['content']]
        self.ws.append(test)
        self.wb.save('chacha.xlsx')

        return item


        # def file_path(self, request, response=None, info=None):
        """
        重命名模块
        """
        # path = os.path.join('D:\\result', ''.join( [request.url.replace('//', '_').replace('/', '_').replace(':', '_').replace('.', '_').replace('__','_'), '.zip']))
        # return path

