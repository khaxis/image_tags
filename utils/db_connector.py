from pymongo import MongoClient

client = MongoClient()
db = client['image_tags']