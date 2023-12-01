import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from scrapy.exceptions import DropItem
from datetime import datetime

class MongoPipeline(object):
    company_schema = 'company_collection'
    user_schema = 'users'

    def open_spider(self, spider):
        load_dotenv(find_dotenv())
        mongo_uri:str = os.getenv("MONGO_URI")
        database_name:str = os.getenv("DATABASE_NAME")

        # print(mongo_uri, database_name)

        self.client = MongoClient(mongo_uri)
        self.db = self.client[database_name]

        try:
            self.client.server_info() 
            print("MongoDB connection successful")
        except Exception as e:
            print("Could not connect to MongoDB: ", e)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Validation
        if not item['name'] or not item['logo'] or not item['address'] or not item['link'] or not item['description']:
            raise DropItem("Missing field in %s" % item)

        # Get user information
        user = self.db[self.user_schema].find_one({"email":"admin@gmail.com"})
        if user:
            item['createdBy'] = {'_id': str(user['_id']), 'email': user['email']}
        else:
            raise DropItem("User not found")

        now = datetime.now().isoformat()

        if not self.db[self.company_schema].find_one({"name": item['name']}):
            item['createdAt'] = now
        item['updatedAt'] = now

        # Transaction
        with self.client.start_session() as session:
            session.start_transaction()
            try:
                self.db[self.company_schema].update_one(
                    {"name": item['name']}, 
                    {"$set": dict(item)}, 
                    upsert=True,
                    session=session
                )
                session.commit_transaction()
            except Exception as e:
                session.abort_transaction()
                raise e

        return item


