from scrapy.cmdline import execute
import os
path = os.path.abspath('.\\scrapytest\\scrapytest\\spiders\\testspider.py')
print(path)
try:
    execute(['scrapy','crawl', 'fojob'])
finally:
    pass
