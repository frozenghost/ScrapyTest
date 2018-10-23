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
import re


class SeleniumMiddleware():
    '''通用selenium下载中间件，通过spider的浏览器访问页面并返回response
    
    Returns:
        HtmlResponse -- 返回载入后的请求
    '''

    def process_request(self, request, spider):
        for cookie_name, cookie_value in request.cookies.items():
            spider.browser.add_cookie({
                'name': cookie_name,
                'value': cookie_value
            })
        if (spider.name == 'fojob'):
            time.sleep(random.randint(1, 7))  # 随机等待
            page = request.meta.get('page', 1)
            need = True  # 最大页数是否大于请求页数
            try:
                spider.browser.get(request.url)
                if page > 1:  # 超过第一页，那么寻找导航条，跳转至对应的页码
                    input = spider.wait.until(  # 输入框
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, '#resultList div.p_in > input')))
                    submit = spider.wait.until(  # 按钮
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR,
                             '#resultList div.p_in > span.og_but')))
                    max_page = spider.browser.find_element_by_xpath(
                        '(//div[@id="resultList"]//div[@class="p_in"]//span[@class="td"])[1]'
                    ).text
                    match = re.search('[1-9]\\d*', max_page)
                    if (match):
                        max_page = match.group()
                    need = int(max_page) >= page
                    input.clear()
                    input.send_keys(page)
                    time.sleep(random.randint(1, 7))
                    if (need):  # 超过最大页数则无需等待处理
                        submit.click()
                        spider.wait.until(
                            EC.text_to_be_present_in_element(
                                (By.CSS_SELECTOR,
                                 '#resultList div.rt > span.dw_c_orange'),
                                str(page)))
                        spider.wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, '#resultList .el')))
                if (need):
                    return HtmlResponse(
                        url=request.url,
                        body=spider.browser.page_source,
                        request=request,
                        encoding='utf-8',
                        status=200)
                else:  # 超出最大页数，返回空（当然还有很多其他做法，个人喜好）
                    return HtmlResponse(
                        url=request.url,
                        request=request,
                        encoding='utf-8',
                        status=200)
            except TimeoutException:
                return HtmlResponse(
                    url=request.url, status=500, request=request)
        elif (spider.name == 'liepin'):
            spider.browser.get(request.url)
            time.sleep(random.randint(1, 5))  # 随机等待
            page = request.meta.get('page', 1)
            try:
                if page > 1:  # 超过第一页，那么寻找导航条，跳转至对应的页码
                    input = spider.wait.until(  # 输入框
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR,
                            'div.pagerbar > span.addition > span.redirect > input')))
                    submit = spider.wait.until(  # 按钮
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR,
                             'div.pagerbar > span.addition > span.redirect > a')))
                    input.clear()
                    input.send_keys(page)
                    time.sleep(random.randint(1, 3))
                    submit.click()
                spider.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.pagerbar > span.addition > span.redirect > a')))
                return HtmlResponse(
                    url=request.url,
                    body=spider.browser.page_source,
                    request=request,
                    encoding='utf-8',
                    status=200)

            except TimeoutException:
                return HtmlResponse(
                    url=request.url, status=500, request=request)


class RandomUserAgent(object):
    '''随机用户请求头

    '''

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        #print "**************************" + random.choice(self.agents)
        request.headers.setdefault('User-Agent', random.choice(self.agents))