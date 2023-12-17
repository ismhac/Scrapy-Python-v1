import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import requests
from scrapy.exceptions import DropItem
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError
import random

class MongoPipeline(object):
    company_module = 'companies'
    job_module = 'jobs'
    user_module = 'users'

    def open_spider(self, spider):
        load_dotenv(find_dotenv())
        mongo_uri:str = os.getenv("MONGO_URI")
        database_name:str = os.getenv("DATABASE_NAME")

        self.client = MongoClient(mongo_uri)
        self.db = self.client[database_name]

        try:
            self.client.server_info() 
            print("Kết nối MongoDB thành công")
        except Exception as e:
            print("Không thể kết nối với MongoDB: ", e)

    def close_spider(self, spider):
        self.client.close()

    # def process_item(self, item, spider):
    #     return item;

    def process_item(self, item, spider):

        array_level =  ["INTERN","FRESHER","JUNIOR","MIDDLE","SENIOR"];

        array_location = ["Hồ Chí Minh","Cần Thơ","Hà Nội","Đà Nẵng","Bình Dương","Hải Phòng","Long An","Huế","Băc Ninh","Đồng Nai","Vũng Tàu","Bình Thuận","Ninh Thuận","Đồng Tháp","An Giang"];

        # Validation
        if not item.get('company_name') or not item.get('company_logo') or not item.get('company_address') or not item.get('company_link') or not item.get('company_description'):
            spider.logger.warning("Thiếu trường trong %s" % item)
            return item

        # Get user information
        user = self.db[self.user_module].find_one({"email": "admin@gmail.com"})
        if user:
            item['company_createdBy'] = {'_id': str(user['_id']), 'email': user['email']}
            item['company_updatedBy'] = {'_id': str(user['_id']), 'email': user['email']}
        else:
            spider.logger.error("Không tìm thấy người dùng cho %s" % item['company_name'])
            return item

        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")

        # Transaction
        with self.client.start_session() as session:
            session.start_transaction()
            try:
                # Update or insert company
                result = self.db[self.company_module].update_one(
                    {"name": item['company_name'], "isDeleted": False},
                    {"$set": {
                        "name": item['company_name'],
                        "address": item['company_address'],
                        "description": item['company_description'],
                        "logo": item['company_logo'],
                        # 
                        "createdBy": item['company_createdBy'],
                        "createdAt": formatted_now,
                        "updatedAt": formatted_now,
                        "isDeleted": False,
                        "deletedAt": None,
                        "updatedBy": item['company_updatedBy'],
                        "deletedBy": None
                        }
                    },
                    upsert=True,
                    session=session
                )

                # Get the company_id
                if result.upserted_id is not None:
                    company_id = result.upserted_id
                else:
                    company = self.db[self.company_module].find_one({"name": item['company_name'], "isDeleted": False})
                    company_id = company['_id']

                # Store jobs information
                for job in item.get('jobs', []):

                    description = ""
                    
                    temp_job_description = requests.get(f'https://api.topdev.vn/td/v2/companies/{item['company_id']}/jobs/?fields[job]=requirements,id')
                    temp_job_description_data_json = temp_job_description.json()

                    for job_item in temp_job_description_data_json.get('data'):
                        # print(f"item id: {job_item.get('id')}, temp_job_id: {job['job_id']}")
                        description += f"<div>{job_item.get('requirements')}</div>"
                        print(description)
                
                        # if job['job_id'] == job_item.get('id'):
                        #     print("Found matching id")
                        #     description += f"<div>{job_item.get('requirements')}</div>"
                        #     print(f"description: {description}")
                        #     break;

                    self.db[self.job_module].update_one(
                        {"name": job['job_name'], "isDeleted": False},
                        {"$set": {
                            "name": job['job_name'],
                            "skills": job['job_skills'],
                            "company": company_id,
                            "likedUsers": [],
                            "appliedUsers": [],
                            "location": random.choice(array_location),
                            "salary": random.randint(10,30) * 1000000,
                            "quantity": 1,
                            "level": random.choice(array_level),
                            # "description": job['job_description'],
                            "description": description,
                            "startDate": formatted_now,
                            "endDate":  (now + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S.000+00:00"),
                            "isActive": True,
                             # 
                            "createdBy": item['company_createdBy'],
                            "createdAt": formatted_now,
                            "updatedAt": formatted_now,
                            "isDeleted": False,
                            "deletedAt": None,
                            "updatedBy": item['company_updatedBy'],
                            "deletedBy": None
                        }},
                        upsert=True,
                        session=session
                    )
                session.commit_transaction()

            except Exception as e:
                session.abort_transaction()
                spider.logger.error("Lỗi khi xử lý mục: %s" % e)

        return item
