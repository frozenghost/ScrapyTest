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
import random
import scrapy


class Fojobspider(Spider):
    name = "fojob"
    allowed_domains = ["www.51job.com"]
    base_url = "https://search.51job.com/list/020000,000000,0000,00,9,%02d,%s,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99%s&lonlat=0%%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="

    custom_settings = {
        'KEYWORDS': ['.net'],
        'MAX_PAGE': 100,
        'SALARY_RANGE': [FO_Salary.S_20K_30k, FO_Salary.S_30k_40k]
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
                for page in range(1, 10):  # 取前10页数据
                    url = self.base_url % (salary.value, quote(keyword), '' if
                                           (salary != FO_Salary.ALL) else
                                           '&providesalary=99')
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        meta={"page": page},
                        dont_filter=True)

    def parse(self, response):
        products = response.xpath(
            '//div[@id="resultList"]//div[@class="el" or @class="el mk"]')
        for product in products:
            item = JobItem()
            item['name'] = ''.join(
                product.xpath('.//p[contains(@class, "t1")]//span//a/@title').
                extract()).strip()
            item['company'] = ''.join(
                product.xpath('.//span[contains(@class, "t2")]//a/@title').
                extract()).strip()
            item['area'] = product.xpath(
                './/span[contains(@class, "t3")]//text()').extract_first()
            item['salary'] = product.xpath(
                './/span[contains(@class, "t4")]//text()').extract_first()
            item['publishdate'] = product.xpath(
                './/span[contains(@class, "t5")]//text()').extract_first()
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