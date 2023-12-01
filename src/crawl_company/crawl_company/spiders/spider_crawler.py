from typing import Any, Iterable
import scrapy
from scrapy.http import Request, Response

class Company(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    logo = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    createdBy  = scrapy.Field()
    isDeleted = scrapy.Field()
    createdAt = scrapy.Field()
    updatedAt = scrapy.Field()
    deletedAt = scrapy.Field()

class crawling(scrapy.Spider):
    name = "crawl_company"
    def start_requests(self) -> Iterable[Request]:
        url = "https://topdev.vn/nha-tuyen-dung?src=topdev.vn&medium=mainmenu.html"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        links = response.xpath("//div[@id='post_data']//div[@class='frame style-2']/a[@class='link']//@href").extract()
        # print(links)
        domain = "https://topdev.vn"
        for url in links:
            full_link = domain + url.strip()
            yield scrapy.Request(url=full_link, callback=self.parse_company)
    
    def parse_company(self, response: Response, **kwargs: Any) -> Any:
        items = Company()

        name = response.xpath('//div[@id="common-information"]/div/div[2]/h1//text()').get()

        logo = response.xpath('//div[@id="common-information"]/div/div[1]/img//@src').get()

        address = response.xpath('//main[@id="company-detail-page"]/div[@class="container"]/div[@class="grid grid-cols-3 gap-6"]/div[@class="col-span-1"]/div[@class="py-6"]/div[@class="mt-4"]/div[@class="rounded bg-white"]/div[@class="p-4 pt-0"]//div[@class="mt-4"]/ul[@class="mt-2"]/li/div[@class="rounded border border-solid border-white p-2 transition-all"]/div[@class="flex items-start gap-2"]/p[@class="flex-1"]//text()').get()

        description = ''.join(response.xpath('//section[@id="company-profile"]/*').get())

        # print(name)
        # print(logo)
        # print(address)
        
        items['name'] = name
        items['logo'] = logo
        items['address'] = address
        items['link'] = response.url
        items['description'] = description
        yield items
