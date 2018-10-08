# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from openpyxl import Workbook
import urlparse

import time

class TutorialPipeline(object):

    def __init__(self):

        self.wb = Workbook()
        self.ws = self.wb.active
        self.name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        self.ws.append(['标题', '发文体系', '文号', '序号',
                        '公示类型', '进度', '类型', '适用地区',
                        '发文时间', '扶持金额', '有效期限', '适用行业',
                        '政策分类', '申报详情', '附件列表', '文章地址'])  # 设置表头


    def parseT(self, value):
                return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):
        test = [
                item['title'],      item['system'],     item['number'],     item['index'],
                item['notetype'],   item['progress'],   item['type'],       item['area'],
                item['updateTime'], item['money'],      item['validTime'],  item['industry'],
                item['policyType'], item['content'],    "",                 item['url']
        ]
        self.ws.append(test)

        query = str(urlparse.urlparse(spider.browser.current_url).query)
        queryParams = dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])

        # searchName = ''
        # query = urlparse.urlparse(spider.browser.current_url).query
        # for value in query.split('&'):
        #     nameValue = value.split('=')
        #     if nameValue[0] == 'query_text':
        #         searchName = urllib.unquote(str(nameValue[1].decode('unicode_escape')))
        #         break

        self.wb.save(spider.location + self.name + '-' + queryParams['query_text'].decode('utf-8') + '.xlsx')

        return item



