from typing import Any, Iterable
import scrapy
from scrapy.http import Request, Response
import json
import re
import requests

class Company(scrapy.Item):
    company_link = scrapy.Field()
    company_name = scrapy.Field()
    company_address = scrapy.Field()
    company_description = scrapy.Field()
    company_logo = scrapy.Field()

    company_createdBy  = scrapy.Field()
    company_updatedBy = scrapy.Field()
    company_deletedBy = scrapy.Field()

    company_isDeleted = scrapy.Field()
    company_createdAt = scrapy.Field()
    company_updatedAt = scrapy.Field()
    company_deletedAt = scrapy.Field()

    company_id = scrapy.Field()
    

    jobs = scrapy.Field()

class Job(scrapy.Item):
    job_name = scrapy.Field()
    job_skills = scrapy.Field() 
    job_link = scrapy.Field()
    job_link_id = scrapy.Field()
    job_description = scrapy.Field()
    job_location = scrapy.Field()
    job_id = scrapy.Field()



class crawling(scrapy.Spider):
    name = "crawl_company"
    domain = "https://topdev.vn"
    def start_requests(self) -> Iterable[Request]:
        url = "https://topdev.vn/nha-tuyen-dung?src=topdev.vn&medium=mainmenu.html"
        yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response: Response, **kwargs: Any) -> Any:
        links = response.xpath("//div[@id='post_data']//div[@class='frame style-2']/a[@class='link']//@href").extract()
        # print(links)
        
        for url in links:
            full_link = self.domain + url.strip()
            yield scrapy.Request(url=full_link, callback=self.parse_company)
    def parse_company(self, response: Response, **kwargs: Any) -> Any:
        company_items = Company()

        company_items['jobs'] = []
        # company
        name = response.xpath('//div[@id="common-information"]/div/div[2]/h1//text()').get()
        logo = response.xpath('//div[@id="common-information"]/div/div[1]/img//@src').get()
        address = response.xpath('//main[@id="company-detail-page"]/div[@class="container"]/div[@class="grid grid-cols-3 gap-6"]/div[@class="col-span-1"]/div[@class="py-6"]/div[@class="mt-4"]/div[@class="rounded bg-white"]/div[@class="p-4 pt-0"]//div[@class="mt-4"]/ul[@class="mt-2"]/li/div[@class="rounded border border-solid border-white p-2 transition-all"]/div[@class="flex items-start gap-2"]/p[@class="flex-1"]//text()').get()
        description = ''.join(response.xpath('//section[@id="company-profile"]/*').extract())

        
        company_items['company_name'] = name
        company_items['company_address'] = address
        company_items['company_description'] = description
        company_items['company_logo'] = logo
        company_items['company_link'] = response.url

        # jobs
        job_urls = response.xpath('//section[@id="opening-jobs"]/div[@class="mt-6"]/ul//li[@class="mb-4 last:mb-0"]/div[@class="rounded border border-solid border-gray-200 bg-white p-4 transition-all hover:shadow-sm"]/div[@class="flex items-start justify-between gap-2"]/div[@class="flex-1"]/h3[@class="line-clamp-1 text-sm font-bold lg:text-base"]/a[@class="transition-all hover:text-primary"]//@href').extract()
        
        for url in job_urls:
            full_link = self.domain + url.strip()
            request =  scrapy.Request(
                url=full_link, 
                callback=self.parse_job_link)
            request.meta['company'] = company_items
            yield request
            
    def parse_job_link(self, response: Response, **kwargs: Any) -> Any:
        job_items = Job()

        company = response.meta['company']

        link = response.url

        # Get id of job 
        temp_job_link =  re.findall(r'\d+', link)
        temp_job_id = temp_job_link[-1]

        name = response.xpath('//section[@id="detailJobHeader"]/div[@class="w-3/4 flex flex-initial flex-col"]/h1[@class="text-2xl font-bold text-black"]//text()').get()

        # Extract the script tag data
        script_data = response.xpath('//script[@type="application/ld+json"][2]/text()').get()
        # Parse the JSON data
        json_data = json.loads(script_data)
        skills_string = json_data.get('skills')
        skills = skills_string.split(', ') if skills_string else []

        description = ""

        # print(response.url)
        # description = ''.join(response.xpath('//section[@class="content"]/section[@id="cardContentDetailJob"]/*').extract())

        #  Get id of company
        temp_company_link = company['company_link']
        match = re.findall(r'\d+', temp_company_link)
        temp_company_id = match[-1] if match else None

        # temp_job_description = requests.get(f'https://api.topdev.vn/td/v2/companies/{temp_company_id}/jobs/?fields[job]=requirements,id')
        # temp_job_description_data_json = temp_job_description.json()

        # # print(temp_job_description_data_json.get('data'))  

        # for item in temp_job_description_data_json.get('data'):
        #     print(f"item id: {item.get('id')}, temp_job_id: {temp_job_id}")
    
        #     if temp_job_id == item.get('id'):
        #         print("Found matching id")
        #         description += f"<div>{item.get('requirements')}</div>"
        #         print(f"description: {description}")
        #         break;



            # if item.get('id') == temp_job_id: 
            #     requirements = item.get('requirements')
            #     if requirements:
            #     # Thêm requirements vào thẻ div
            #         description += f'<div>{requirements}</div>'
    
        job_items['job_link'] = link
        job_items['job_name'] = name
        job_items['job_skills'] = skills
        # items['job_link_id'] = link_id
        job_items['job_description'] = description
        job_items['job_id'] = temp_job_id

        # company = response.meta['company']
        company['jobs'].append(job_items)
        company['company_id'] = temp_company_id

        yield company



        

