from flask import current_app
from pymongo import MongoClient

client = None
db = None

def init_db():
    global client, db
    client = MongoClient("mongodb://localhost:27017/")
    db = client["anime_db"] 

def get_db():
    return db