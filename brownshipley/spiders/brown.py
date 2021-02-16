import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from brownshipley.items import Article


class BrownSpider(scrapy.Spider):
    name = 'brown'
    start_urls = ['https://brownshipley.com/en-gb/news-and-insights']

    def parse(self, response):
        articles = response.xpath('//div[@class="l-col-3__col"]')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('.//div[@class="c-card__date"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        if date:
            date = datetime.strptime(date.strip(), '%d %B %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="l-section l-section--left-alignment"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
