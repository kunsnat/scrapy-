#coding:utf-8
from scrapy.cmdline import execute
import sys
import os


reload(sys)
sys.setdefaultencoding('utf-8')

while True:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy","crawl","chacha"])

