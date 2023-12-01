from typing import Any, Iterable
import scrapy
from scrapy.http import Request, Response

class Company(scrapy.Item):
    Name = scrapy.Field()
    Logo = scrapy.Field()
    Address = scrapy.Field()

class crawling(scrapy.Spider):
    name = "demo"
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
        address = response.xpath('//main[@id="company-detail-page"]//div//div//div[2]//div//div[2]//div//div[2]//div[3]//ul//li//div//div//p//text()').get()
        # print(name)
        # print(logo)
        print(address)
        items['Name'] = name
        items['Logo'] = logo
        items['Address'] = address
        yield items
