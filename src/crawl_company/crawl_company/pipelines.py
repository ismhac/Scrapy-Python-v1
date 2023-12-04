import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from scrapy.exceptions import DropItem
from datetime import datetime
from pymongo.errors import DuplicateKeyError

class MongoPipeline(object):
    company_module = 'company_collection'
    job_module = 'job_collection'
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

    def process_item(self, item, spider):
        # Validation
        if not item.get('company_name') or not item.get('company_logo') or not item.get('company_address') or not item.get('company_link') or not item.get('company_description'):
            spider.logger.warning("Thiếu trường trong %s" % item)
            return item

        # Get user information
        user = self.db[self.user_module].find_one({"email": "admin@gmail.com"})
        if user:
            item['company_createdBy'] = {'_id': str(user['_id']), 'email': user['email']}
        else:
            spider.logger.error("Không tìm thấy người dùng cho %s" % item['company_name'])
            return item

        now = datetime.now().isoformat()

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
                        "createdBy": item['company_createdBy'],
                        "createdAt": now,
                        "updatedAt": now,
                        "isDeleted": False,
                        "deletedAt": None
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
                    self.db[self.job_module].update_one(
                        {"name": job['job_name'], "isDeleted": False},
                        {"$set": {
                            "name": job['job_name'],
                            "skills": job['job_skills'],
                            "company": {
                                "_id": company_id,
                                "name": item['company_name'],
                                "logo": item['company_logo']
                            }
                        }},
                        upsert=True,
                        session=session
                    )

                session.commit_transaction()

            except Exception as e:
                session.abort_transaction()
                spider.logger.error("Lỗi khi xử lý mục: %s" % e)

        return item
