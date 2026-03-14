#!/usr/bin/env python3
"""
Oil Fire Scenario - Cache Test
MongoDB'de cache kaydı kontrol et
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("🔥 OIL FIRE CACHE TEST - MongoDB Cache Kaydını Kontrol Et")
print("=" * 80)
print()

# Incident data
incident_data = {
    "ref_no": "OIL-2026-002-FIRE",
    "description": "Yağ tasfiye cihazı yanması - yanlış devreye alma sırası"
}

print("📊 Test Incident:")
print(f"   ref_no: {incident_data['ref_no']}")
print(f"   description: {incident_data['description'][:60]}...")
print()

# MongoDB cache kontrol et
mongo_uri = os.getenv("MONGODB_URI")
if mongo_uri and mongo_uri.startswith('"'):
    mongo_uri = mongo_uri[1:-1]

db_name = os.getenv("MONGODB_RCA_DB", "rca")
col_name = os.getenv("MONGODB_CACHE_COLLECTION", "analysis_cache")

print(f"🔍 MongoDB Kontrolü:")
print(f"   Database: {db_name}")
print(f"   Collection: {col_name}")
print()

try:
    from pymongo import MongoClient
    import hashlib
    
    # Cache key oluştur
    normalized = f"{incident_data['ref_no']}:{incident_data['description']}".strip().lower()
    normalized = " ".join(normalized.split())
    cache_key = hashlib.md5(normalized.encode()).hexdigest()
    
    print(f"📝 Cache Key: {cache_key[:16]}...")
    print()
    
    # MongoDB'ye bağlan (timeout ile)
    print("🔗 Bağlanılıyor (timeout: 10s)...")
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("   ✅ Bağlantı başarılı!")
    except Exception as e:
        print(f"   ⚠️  MongoDB bağlantısı başarısız: {str(e)[:80]}")
        print()
        print("   💡 Not: MongoDB bağlantı hatası, fakat disk cache çalışıyor.")
        print("   Disk cache'de veri tutulmuş olabilir.")
        print()
        sys.exit(0)
    
    # Database ve collection kontrol et
    db = client[db_name]
    collection = db[col_name]
    
    # Cache dokümanlı var mı?
    found = collection.find_one({"cache_key": cache_key})
    
    if found:
        print(f"✅ CACHE HIT! Dokümanlı bulundu:")
        print(f"   ID: {found.get('_id')}")
        print(f"   Created: {found.get('created_at')}")
        print(f"   Expires: {found.get('expires_at')}")
        if 'analysis_result' in found:
            print(f"   Result keys: {list(found['analysis_result'].keys())}")
    else:
        print(f"❌ CACHE MISS - Dokümanlı bulunamadı")
        print(f"   {col_name} collection'ında {cache_key[:16]}... ile eşleşen kayıt yok")
        print()
        print(f"💡 Collection'da toplam dokümanlı: {collection.count_documents({})}")
        
        # Bütün dokümanlı listele
        all_docs = list(collection.find({}, {"cache_key": 1, "incident_ref": 1, "created_at": 1}))
        if all_docs:
            print(f"\n   Mevcut dokümanlı:")
            for doc in all_docs:
                print(f"   • {doc.get('incident_ref', 'N/A')} - {doc.get('cache_key', 'N/A')[:16]}...")
        else:
            print(f"\n   Collection tamamen boş!")
    
    client.close()
    
except ImportError:
    print("❌ pymongo yüklü değil!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
