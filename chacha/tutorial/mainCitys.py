#coding:utf-8
from scrapy.cmdline import execute
import sys
import os
import time
import datetime
import platform

from chacha.tutorial import logger
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # ide调试
execute(["scrapy","crawl","citys"])






