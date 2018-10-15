import scrapy
from customer_constant import FO_Salary
from scrapy import Request, Spider
from urllib.parse import quote
from scrapy.utils.project import get_project_settings
from items import JobItem


class Fojobspider(Spider):
    name = "fojob"
    allowed_domains = ["www.51job.com"]
    base_url = "https://search.51job.com/list/020000,000000,0000,00,9,%02d,%s,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99%s&lonlat=0%%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="

    custom_settings = {'KEYWORDS': ['.net'], 'MAX_PAGE': 100, 'SALARY_RANGE':[FO_Salary.S_20K_30k, FO_Salary.S_30k_40k]}

    def start_requests(self):
        for keyword in self.custom_settings['KEYWORDS']:
            for salary in self.custom_settings['SALARY_RANGE']:
                for page in range(1, 10):
                    url = self.base_url % (salary.value, quote(keyword), '' if(salary != FO_Salary.ALL) else '&providesalary=99')
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
                product.xpath(
                    './/p[contains(@class, "t1")]//span//a/@title').
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