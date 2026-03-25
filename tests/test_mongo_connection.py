#!/usr/bin/env python3
"""
MongoDB Bağlantı Diagnostiği
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("MongoDB Atlas Bağlantı Diagnostiği")
print("=" * 60)

# 1. Environment variables kontrol
print("\n1️⃣  Environment Variables:")
mongo_uri = os.getenv("MONGODB_URI", "").strip()
if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
    mongo_uri = mongo_uri[1:-1]

if mongo_uri:
    print(f"   ✅ MONGODB_URI ayarlanmış")
    print(f"   Host: {mongo_uri.split('@')[1].split('/')[0] if '@' in mongo_uri else 'N/A'}")
else:
    print(f"   ❌ MONGODB_URI ayarlanmamış")

print(f"   Database: {os.getenv('MONGODB_RCA_DB', 'N/A')}")
print(f"   Collection: {os.getenv('MONGODB_CACHE_COLLECTION', 'N/A')}")

# 2. PyMongo check
print("\n2️⃣  PyMongo Paketi:")
try:
    import pymongo
    print(f"   ✅ pymongo yüklü (v{pymongo.__version__})")
except ImportError:
    print(f"   ❌ pymongo yüklü değil")
    sys.exit(1)

# 3. Bağlantı testi (timeout ile)
print("\n3️⃣  MongoDB Bağlantı Testi:")
print("   Bağlanılıyor (max 10 saniye)...")

try:
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    import socket
    
    # DNS resolve test
    try:
        host = mongo_uri.split('@')[1].split('/')[0] if '@' in mongo_uri else None
        if host:
            print(f"   DNS çözümleme: {host}")
            ip = socket.gethostbyname(host)
            print(f"   ✅ DNS resolved: {ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS çözümleme hatası: {e}")
    except Exception as e:
        print(f"   ⚠️  DNS test hatası: {e}")
    
    # MongoDB connection
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    
    # Ping test
    client.admin.command('ping')
    print(f"   ✅ MongoDB'ye bağlantı başarılı!")
    
    # Database info
    db_name = os.getenv("MONGODB_RCA_DB", "rca_database")
    db = client[db_name]
    
    print(f"\n4️⃣  Database Bilgileri:")
    print(f"   Database: {db_name}")
    
    collections = db.list_collection_names()
    print(f"   Collections: {collections}")
    
    # Cache collection check
    cache_col = os.getenv("MONGODB_CACHE_COLLECTION", "analysis_cache")
    if cache_col in collections:
        doc_count = db[cache_col].count_documents({})
        print(f"   ✅ {cache_col}: {doc_count} dokümanlı")
    else:
        print(f"   ℹ️  {cache_col}: Henüz oluşturulmamış (ilk yazı ile oluşacak)")
    
    client.close()
    print("\n✅ Bağlantı başarılı!")
    
except ServerSelectionTimeoutError as e:
    print(f"   ❌ TIMEOUT: MongoDB'ye bağlanılamıyor")
    print(f"      {e}")
    print("\n🔍 Sorun Kaynakları:")
    print("   • Network/Firewall engeli")
    print("   • MongoDB Atlas whitelist ayarları")
    print("   • İnternet bağlantısı yok")
    print("   • Yanlış URI")
    
except Exception as e:
    print(f"   ❌ Hata: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
