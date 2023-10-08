# mongo.py
from pymongo import MongoClient

client = MongoClient().mail
arxiv_db = client.arxiv

# arxiv_db.delete_many({})