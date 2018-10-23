from customer_constant import FO_Salary
from scrapy import Request, Spider, signals
from urllib.parse import quote
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from items import JobItem
from settings import PROXIES
from datetime import datetime
import random
import scrapy


class Liepinspider(Spider):
    name = "liepin"
    displayname = '猎聘'
    allowed_domains = ["www.liepin.com"]
    base_url = "https://www.liepin.com/zhaopin/?ckid=9a3c3f6ae39c891b&fromSearchBtn=2&init=-1&sfrom=click-pc_homepage-centre_searchbox-search_new&flushckid=1&dqs=020&curPage=0&degradeFlag=0%s&key=%s&headckid=8f96e572ab75696a&d_pageSize=40&siTag=LVCXL87NN2EpVFUH8QYgiQ~r3i1HcfrfE3VRWBaGW6LoA&d_headId=40efa97cbb8f79744109ade811cde239&d_ckId=7a3f32c501149efa365d5baa1b674be9&d_sfrom=search_fp&d_curPage=0"

    custom_settings = {
        'KEYWORDS': ['.net'],
        'MAX_PAGE': 50,
        'SALARY_RANGE': ['20$30', '30$50', '50$100', '100$999']
    }

    def __init__(self, timeout=None, service_args=[]):
        chromeoption = webdriver.ChromeOptions()
        for option in service_args:
            chromeoption.add_argument(option)
        # proxy = random.choice(PROXIES)
        # chromeoption.add_argument('--proxy-server=' + proxy['ip_port'])
        self.timeout = timeout
        self.browser = webdriver.Chrome(chrome_options=chromeoption)
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def start_requests(self):
        for keyword in self.custom_settings['KEYWORDS']:  # 职位关键字
            for salary in self.custom_settings['SALARY_RANGE']:  # 薪资范围
                for page in range(1, self.custom_settings['MAX_PAGE']):
                    url = self.base_url % ('' if (salary == '') else
                                           ('&salary=' + quote(salary)),
                                           quote(keyword))
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        meta={"page": page},
                        dont_filter=True)

    def parse(self, response):
        products = response.xpath('//ul[@class="sojob-list"]//li')
        for product in products:
            item = JobItem()
            item['name'] = product.xpath(
                './/div[@class="sojob-item-main clearfix"]//div[@class="job-info"]//h3//a//text()'
            ).extract_first().strip()
            item['company'] = product.xpath(
                './/div[@class="sojob-item-main clearfix"]//div[@class="company-info nohover"]//p[@class="company-name"]//a//text()'
            ).extract_first()
            item['area'] = product.xpath(
                './/div[@class="sojob-item-main clearfix"]//div[@class="job-info"]//p[@class="condition clearfix"]//a[@class="area"]//text()'
            ).extract_first()
            item['salary'] = product.xpath(
                './/div[@class="sojob-item-main clearfix"]//div[@class="job-info"]//p[@class="condition clearfix"]//span[@class="text-warning"]//text()'
            ).extract_first()
            item['publishdate'] = product.xpath(
                './/div[@class="sojob-item-main clearfix"]//div[@class="job-info"]//p[@class="time-info clearfix"]//time/@title'
            ).extract_first()
            item['link'] = product.xpath(
                './/div[@class="sojob-item-main clearfix"]//div[@class="job-info"]//h3//a/@href'
            ).extract_first()
            if(not item['link'].startswith('https')):
                item['link'] = 'https://www.liepin.com' + item['link']
            item['source'] = self.displayname
            item['downloaddate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(
            timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
            service_args=crawler.settings.get('CHROME_SERVICE_ARGS'))
        crawler.signals.connect(middleware.spider_closed,
                                signals.spider_closed)  # 信号量关联，spider退出之后关闭浏览器
        return middleware

    def spider_closed(self):
        self.browser.quit()