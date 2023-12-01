import os
from pymongo import MongoClient
from dotenv import load_dotenv

class MongoPipeline(object):
    collection_name = 'company_collection'

    def open_spider(self, spider):
        load_dotenv()
        mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
        self.client = MongoClient(mongo_connection_string)
        self.db = self.client["captainhac"]

        try:
            self.client.server_info() 
            print("MongoDB connection successful")
        except Exception as e:
            print("Could not connect to MongoDB: ", e)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
