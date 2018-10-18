#coding:utf-8
from scrapy.cmdline import execute
import sys
import os
import time
import datetime
import platform

from chacha.tutorial import logger
import logging

# 通过CrawlerProcess同时运行几个spider
from scrapy.crawler import CrawlerProcess
# 导入获取项目配置的模块
from scrapy.utils.project import get_project_settings
# 导入蜘蛛模块(即自己创建的spider)
from chacha.tutorial.spiders.chaxun import QichaSpider

reload(sys)
sys.setdefaultencoding('utf-8')

# execute(["scrapy","crawl","chaxun", "-a", "index=" + str(index)])
# execute(["scrapy","crawl","check"])
# execute(["scrapy","crawl","citys"])
# os.system("scrapy crawl chacha")    # 系统运行 无调试



# get_project_settings() 必须得有，不然"HTTP status code is not handled or not allowed"
process = CrawlerProcess(get_project_settings())
process.crawl(QichaSpider, index=0) # 注意引入
process.crawl(QichaSpider, index=1) # 注意引入
process.start()



# logging.info('test ----> ')

# os_platform = platform.platform()
# if os_platform.startswith('Darwin'):
#     print 'this is linux'
#     os.system('ls')
# elif os_platform.startswith('Window'):
#     print 'this is window'
#     os.system('dir') # 当前目录

# def doSth():
#
#     print('test')
#
#     # 假装做这件事情需要一分钟
#
#     time.sleep(60)

# def main():
#     print '1'
#
#     while True:
#         print '1'


# doSth()





