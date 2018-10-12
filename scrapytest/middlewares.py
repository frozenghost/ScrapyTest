# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from scrapy import signals
from logging import getLogger
import time
import random
import base64
from settings import PROXIES


class SeleniumMiddleware():
    def __init__(self, timeout=None, service_args=[]):
        chromeoption = webdriver.ChromeOptions()
        # for option in service_args:
        #     chromeoption.add_argument(option)
        proxy = random.choice(PROXIES)
        # chromeoption.add_argument('--proxy-server=' + proxy['ip_port'])

        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.browser = webdriver.Chrome()
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def process_request(self, request, spider):
        """
        用PhantomJS抓取页面
        :param request: Request对象
        :param spider: Spider对象
        :return: HtmlResponse
        """
        for cookie_name, cookie_value in request.cookies.items():
            self.browser.add_cookie({
                'name': cookie_name,
                'value': cookie_value
            })
        time.sleep(random.randint(1, 9))
        page = request.meta.get('page', 1)
        try:
            self.browser.get(request.url)
            if page > 1:
                input = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#resultList div.p_in > input')))
                submit = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         '#resultList div.p_in > span.og_but')))
                input.clear()
                input.send_keys(page)
                time.sleep(random.randint(0, 9))
                submit.click()
            self.wait.until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, '#resultList div.rt > span.dw_c_orange'),
                    str(page)))
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#resultList .el')))
            return HtmlResponse(
                url=request.url,
                body=self.browser.page_source,
                request=request,
                encoding='utf-8',
                status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(
            timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
            service_args=crawler.settings.get('CHROME_SERVICE_ARGS'))
        crawler.signals.connect(middleware.spider_closed,
                                signals.spider_closed)
        return middleware

    def spider_closed(self):
        self.browser.quit()


class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        #print "**************************" + random.choice(self.agents)
        request.headers.setdefault('User-Agent', random.choice(self.agents))