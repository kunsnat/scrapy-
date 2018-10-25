# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from selenium.webdriver.common.keys import Keys

from scrapy.utils.project import get_project_settings


class TutorialSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TutorialDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


#User-agent
class UAMiddleware(object):
    settings = get_project_settings()
    user_agent_list = settings['USER_AGENT_LIST']

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua

#ip
class ProxyMiddleware(object):
    settings = get_project_settings()
    ip_list = settings['IP_LIST']

    def process_request(self, request, spider):
        ip = random.choice(self.ip_list)
        request.meta['proxy'] = ip


from scrapy.http import HtmlResponse
import time
import logging

class JSPageMiddleware(object):

    #通过chrome 动态访问http_proxy
    def process_request(self, request, spider):
        print spider.name + 'load JSPageMiddleware process_request'

        if spider.name =="chaxun":

            if spider.isHyperlink(request.url):
                if spider.needLogin:
                    spider.hyperBrowser.get('https://www.chacha.top/')
                    time.sleep(2) # 预留加载网页时间
                    spider.needLogin = False
                    spider.hyperBrowser.find_element_by_xpath('//a[@class="header-login"]').click()
                    spider.hyperBrowser.find_element_by_xpath('//span[@class="login-tab login-tab-last"]').click()

                    spider.hyperBrowser.find_element_by_xpath('//input[@name="login_phone"]').send_keys("18094202229")
                    spider.hyperBrowser.find_element_by_xpath('//input[@name="login_password"]').send_keys("1234567890")
                    spider.hyperBrowser.find_element_by_xpath('//button[@class="btn-control bg-orange text-white login-btn m-t"]').click()

                    time.sleep(5) # find_element_by_xpath 查询有点慢, 需要等待

                spider.hyperBrowser.get(request.url)
                print 'load hyper'

                return HtmlResponse(url=spider.hyperBrowser.current_url,body=spider.hyperBrowser.page_source,encoding="utf-8")

            else:
                if spider.itemLength == 0:
                    spider.browser.get(request.url)

                logging.info('load main page and down refresh')

                for i in range(1, 80): #
                    spider.browser.find_element_by_xpath("//body").send_keys(Keys.DOWN)

                time.sleep(3)

                return HtmlResponse(url=spider.browser.current_url,body=spider.browser.page_source,encoding="utf-8")

        elif spider.name =="check":
            spider.browser.get(request.url)

            return HtmlResponse(url=spider.browser.current_url,body=spider.browser.page_source,encoding="utf-8")

        elif spider.name == "citys":
            spider.browser.get(request.url)
            time.sleep(1)
            spider.browser.find_element_by_xpath('//input[@id="city"]').click()
            time.sleep(2)

            return HtmlResponse(url=spider.browser.current_url,body=spider.browser.page_source,encoding="utf-8")


    # def downFresh(self, spider):
    #     startLen = len(spider.browser.find_elements_by_xpath('//li[@class="list-item"]'))
    #     print 'start len is -->  %s'
    #
    #     for i in range(1, 100):
    #         spider.browser.find_element_by_xpath("//body").send_keys(Keys.DOWN)
    #
    #     time.sleep(5) # 预留加载时间   新list中的数据记录
    #     endLen = len(spider.browser.find_elements_by_xpath('//li[@class="list-item"]'))
    #     print 'end len is -->  %s'
    #     if startLen != endLen:
    #         self.downFresh(spider)