#coding:utf-8
from scrapy.cmdline import execute
import sys
import os
import time
import datetime
import platform

from chacha.tutorial import logger
import logging

import subprocess

# 通过CrawlerProcess同时运行几个spider
from scrapy.crawler import CrawlerProcess
# 导入获取项目配置的模块
from scrapy.utils.project import get_project_settings
# 导入蜘蛛模块(即自己创建的spider)
from chacha.tutorial.spiders.chaxun import QichaSpider

reload(sys)
sys.setdefaultencoding('utf-8')

# execute(["scrapy","crawl","chaxun", "-a", "index=" + str(1)])

# os.system("scrapy crawl chaxun -a index=1")    # 系统运行 无调试
# os.system("scrapy crawl chaxun -a index=2")    # 顺序执行, 但是没有正常关闭掉浏览器.

# get_project_settings() 必须得有，不然"HTTP status code is not handled or not allowed"

# process.crawl(QichaSpider, index=3)
# process.crawl(QichaSpider, index=4)
# process.crawl(QichaSpider, index=5)
# process.crawl(QichaSpider, index=0)
# process.crawl(QichaSpider, index=2)
# process.crawl(QichaSpider, index=1) # 注意引入

# process = CrawlerProcess(get_project_settings())
# for value in range(5):
#     process.crawl(QichaSpider, index=value)
# process.start()



import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor


test = 0

while True:
    logging.info(" test -------> value is : " + str(test))
    os.system("scrapy crawl chaxun -a index=%s" % test)    # 顺序执行
    test  += 1
    time.sleep(2)  #  定时间隔,  后续可以加入 区域编码等参数  循环执行.       添加和覆盖 . 
    if test > 5:
        break








