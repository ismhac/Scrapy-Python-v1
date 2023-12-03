
# import json
# from typing import Any, Iterable
# import scrapy
# from scrapy.http import Request, Response
# import re

# class Company(scrapy.Item):
#     link = scrapy.Field()

# class Job(scrapy.Item):
#     name = scrapy.Field()
#     link = scrapy.Field()
#     skills = scrapy.Field() 
#     link_id = scrapy.Field()

#     check_xpath_skills = scrapy.Field()

# class crawling(scrapy.Spider):

#     name = "crawl_job"

#     def start_requests(self) -> Iterable[Request]:
#         url = "https://topdev.vn/nha-tuyen-dung?src=topdev.vn&medium=mainmenu.html"
#         yield scrapy.Request(url=url, callback=self.parse)

#     def parse(self, response: Response, **kwargs: Any) -> Any:
#         links = response.xpath("//div[@id='post_data']//div[@class='frame style-2']/a[@class='link']//@href").extract()

#         domain = "https://topdev.vn"

#         for url in links:
#             full_link = domain + url.strip()
#             yield scrapy.Request(url=full_link, callback=self.parse_company_link)

#     def parse_company_link(self, response: Response, **kwargs: Any) -> Any:
#         items = Job()

#         job_links = response.xpath('//section[@id="opening-jobs"]/div[@class="mt-6"]/ul//li[@class="mb-4 last:mb-0"]/div[@class="rounded border border-solid border-gray-200 bg-white p-4 transition-all hover:shadow-sm"]/div[@class="flex items-start justify-between gap-2"]/div[@class="flex-1"]/h3[@class="line-clamp-1 text-sm font-bold lg:text-base"]/a[@class="transition-all hover:text-primary"]//@href').extract()

#         domain = "https://topdev.vn"

#         for url in job_links:
#             full_link = domain + url.strip()
#             yield scrapy.Request(url=full_link, callback=self.parse_job_link)

#     def parse_job_link(self, response: Response, **kwargs: Any) -> Any:
#         items = Job()

#         link = response.url

#         id_company =  re.findall(r'\d+', link)
#         link_id = id_company[-1]

#         print(f'check link_id: {link_id}')

#         name = response.xpath('//section[@id="detailJobHeader"]/div[@class="w-3/4 flex flex-initial flex-col"]/h1[@class="text-2xl font-bold text-black"]//text()').get()

#         # Extract the script tag data
#         script_data = response.xpath('//script[@type="application/ld+json"][2]/text()').get()

#         # Parse the JSON data
#         json_data = json.loads(script_data)

#         json_data_2 = json.dumps(json_data)
#         skills = json.loads(json_data_2)['skills']

#         # print(f'check json_data: {json_data_2}')

#         items['link'] = link
#         items['name'] = name
#         items['skills'] = skills
#         items['link_id'] = link_id

#         yield items

import json
from typing import Any, Iterable
import scrapy
from scrapy.http import Request, Response
import re

class Company(scrapy.Item):
    link = scrapy.Field()

class Job(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    skills = scrapy.Field() 
    link_id = scrapy.Field()

class crawling(scrapy.Spider):

    name = "crawl_job"

    def start_requests(self) -> Iterable[Request]:
        url = "https://topdev.vn/nha-tuyen-dung?src=topdev.vn&medium=mainmenu.html"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        links = response.xpath("//div[@id='post_data']//div[@class='frame style-2']/a[@class='link']//@href").extract()

        domain = "https://topdev.vn"

        for url in links:
            full_link = domain + url.strip()
            yield scrapy.Request(url=full_link, callback=self.parse_company_link)

    def parse_company_link(self, response: Response, **kwargs: Any) -> Any:
        
        job_links = response.xpath('//section[@id="opening-jobs"]/div[@class="mt-6"]/ul//li[@class="mb-4 last:mb-0"]/div[@class="rounded border border-solid border-gray-200 bg-white p-4 transition-all hover:shadow-sm"]/div[@class="flex items-start justify-between gap-2"]/div[@class="flex-1"]/h3[@class="line-clamp-1 text-sm font-bold lg:text-base"]/a[@class="transition-all hover:text-primary"]//@href').extract()

        domain = "https://topdev.vn"

        for url in job_links:
            full_link = domain + url.strip()
            request =  scrapy.Request(url=full_link, callback=self.parse_job_link)
            yield request

    def parse_job_link(self, response: Response, **kwargs: Any) -> Any:
        items = Job()

        link = response.url

        id_company =  re.findall(r'\d+', link)
        link_id = id_company[-1]

        # print(f'check link_id: {link_id}')

        name = response.xpath('//section[@id="detailJobHeader"]/div[@class="w-3/4 flex flex-initial flex-col"]/h1[@class="text-2xl font-bold text-black"]//text()').get()

        # Extract the script tag data
        script_data = response.xpath('//script[@type="application/ld+json"][2]/text()').get()

        # Parse the JSON data
        json_data = json.loads(script_data)

        # json_data_2 = json.dumps(json_data).replace("'", '"')
        json_data_2 = json.dumps(json_data)
        skills_string = json.loads(json_data_2).get('skills')
        skills = skills_string.split(', ') if skills_string else []

        # print(f'check json_data: {json_data_2}')

        items['link'] = link
        items['name'] = name
        items['skills'] = skills
        items['link_id'] = link_id

        yield items

