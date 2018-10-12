import scrapy
from scrapy import Request,Spider
from urllib.parse import quote
from scrapy.utils.project import get_project_settings
from items import ProductItem

class TestSpider(Spider):
    name = "test"
    allowed_domains = ["www.taobao.com"]
    base_url = "https://s.taobao.com/search?initiative_id=staobaoz_20181011&q="

    custom_settings = {
        'KEYWORDS': ['Note8'],
        'MAX_PAGE': 100
    }

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get("MAX_PAGE")):
                url = self.base_url + quote(keyword)
                yield scrapy.Request(url=url, callback=self.parse, meta={"page": page}, dont_filter=True)

    def parse(self, response):
        products = response.xpath(
            '//div[@id="mainsrp-itemlist"]//div[@class="items"][1]//div[contains(@class, "item")]')
        for product in products:
            item = ProductItem()
            item['price'] = ''.join(product.xpath('.//div[contains(@class, "price")]//text()').extract()).strip()
            item['title'] = ''.join(product.xpath('.//div[contains(@class, "title")]//text()').extract()).strip()
            item['shop'] = ''.join(product.xpath('.//div[contains(@class, "shop")]//text()').extract()).strip()
            item['image'] = ''.join(product.xpath('.//div[@class="pic"]//img[contains(@class, "img")]/@data-src').extract()).strip()
            item['deal'] = product.xpath('.//div[contains(@class, "deal-cnt")]//text()').extract_first()
            item['location'] = product.xpath('.//div[contains(@class, "location")]//text()').extract_first()
            yield item