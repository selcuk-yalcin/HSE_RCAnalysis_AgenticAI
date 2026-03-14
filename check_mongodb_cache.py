#!/usr/bin/env python3
"""
MongoDB Cache - Tüm Records Kontrol Et
"""
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', '').strip()
if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
    mongo_uri = mongo_uri[1:-1]

db_name = os.getenv('MONGODB_RCA_DB', 'rca')
col_name = os.getenv('MONGODB_CACHE_COLLECTION', 'analysis_cache')

print('MongoDB Cache Kontrol')
print('=' * 80)
print(f'Database: {db_name}')
print(f'Collection: {col_name}')
print()

try:
    from pymongo import MongoClient
    from datetime import datetime, timedelta
    
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
    client.admin.command('ping')
    
    db = client[db_name]
    collection = db[col_name]
    
    # Toplam dokümanlı sayısı
    total = collection.count_documents({})
    print(f'Toplam Cache Records: {total}')
    print()
    
    if total > 0:
        print('Cache Records:')
        print('-' * 80)
        
        for doc in collection.find().sort('created_at', -1):
            print(f'Incident: {doc.get("incident_ref", "N/A")}')
            print(f'  Cache Key: {doc.get("cache_key", "N/A")[:16]}...')
            print(f'  Created: {doc.get("created_at")}')
            print(f'  Expires: {doc.get("expires_at")}')
            
            # TTL kontrol et
            now = datetime.now(doc.get("created_at").tzinfo) if hasattr(doc.get("created_at"), 'tzinfo') else datetime.utcnow()
            expires = doc.get("expires_at")
            
            if expires:
                remaining = (expires - now).total_seconds() / 3600
                print(f'  Remaining: {remaining:.1f} hours')
            
            print()
    
    client.close()
    print('OK!')
    
except Exception as e:
    print(f'HATA: {e}')
