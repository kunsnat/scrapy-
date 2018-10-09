#coding:utf-8
from scrapy.cmdline import execute
import sys
import os
import time
import datetime
import platform

from chacha.tutorial import logger

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # ide调试
# execute(["scrapy","crawl","chacha"])
execute(["scrapy","crawl","check"])

# os.system("scrapy crawl chacha")    # 系统运行 无调试

print '----> 路径信息 ' + os.getcwd()
print '----> 路径信息 '  + os.path.abspath(os.path.join(os.getcwd(), "../.."))

logger.info('test')

# os_platform = platform.platform()
# if os_platform.startswith('Darwin'):
#     print 'this is linux'
#     os.system('ls')
# elif os_platform.startswith('Window'):
#     print 'this is window'
#     os.system('dir') # 当前目录

def doSth():

    print('test')

    # 假装做这件事情需要一分钟

    time.sleep(60)

# def main():
#     print '1'
#
#     while True:
#         print '1'


doSth()





