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

print range(6)


# get_project_settings() 必须得有，不然"HTTP status code is not handled or not allowed"
process = CrawlerProcess(get_project_settings())

for index in range(5):
    process.crawl(QichaSpider, index)

# process.crawl(QichaSpider, index=3)
# process.crawl(QichaSpider, index=4)
# process.crawl(QichaSpider, index=5)
# process.crawl(QichaSpider, index=0)
# process.crawl(QichaSpider, index=2)
# process.crawl(QichaSpider, index=1) # 注意引入
process.start()







