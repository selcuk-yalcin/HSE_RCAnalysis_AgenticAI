#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', '').strip()
if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
    mongo_uri = mongo_uri[1:-1]

print('Test baslıyor...')
print(f'URI: {mongo_uri[:80]}...')

try:
    from pymongo import MongoClient
    print('Baglanıyor (max 10 saniye)...')
    
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    
    print('OK - MongoDB baglandı!')
    
    db_name = os.getenv('MONGODB_RCA_DB', 'rca')
    db = client[db_name]
    
    print('Database: ' + str(db_name))
    print('Collections: ' + str(db.list_collection_names()))
    
    client.close()
    
except Exception as e:
    print('HATA: ' + str(e))
    sys.exit(1)
