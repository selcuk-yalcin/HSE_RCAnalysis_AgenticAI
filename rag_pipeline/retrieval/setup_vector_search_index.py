"""
MongoDB Atlas Vector Search Index Oluşturma
============================================

Bu script, taxonomy koleksiyonunda vektör arama için bir Atlas Search index'i oluşturur.
Bu index, cosine similarity kullanarak hızlı benzerlik aramaları sağlar.

Kullanım:
    python rag_pipeline/retrieval/setup_vector_search_index.py
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Ortam değişkenlerini yükle
load_dotenv()


def create_vector_search_index():
    """MongoDB Atlas Search index'ini oluşturur."""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI ortam değişkeni bulunamadı.")
    
    print("=" * 70)
    print("🔍 MongoDB Atlas Vector Search Index Oluşturucu")
    print("=" * 70)
    print("\n🗄️ MongoDB'ye bağlanılıyor...")
    
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    
    try:
        # Ping ile bağlantıyı test et
        client.admin.command('ping')
        print("✓ MongoDB bağlantısı başarılı!")
    except Exception as e:
        print(f"❌ MongoDB bağlantısı başarısız: {e}")
        raise
    
    db = client.rca
    collection = db.taxonomy
    
    # Vector Search Index tanımı
    index_definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "similarity": "cosine",
                "dimensions": 384  # paraphrase-multilingual-MiniLM-L12-v2 boyutu
            },
            {
                "type": "filter",
                "path": "code"
            },
            {
                "type": "filter",
                "path": "cause_type"
            },
            {
                "type": "filter",
                "path": "content"
            }
        ]
    }
    
    index_name = "taxonomy_vector_search"
    
    try:
        print(f"\n📝 Vector Search index tanımı oluşturuluyor: '{index_name}'")
        print("   - Field: embedding (vector, cosine similarity, 384 dimensions)")
        print("   - Filter fields: code, cause_type, content")
        
        # Mevcut index'i kontrol et
        try:
            existing_indexes = list(collection.list_search_indexes())
            index_exists = any(idx.get('name') == index_name for idx in existing_indexes)
        except Exception:
            index_exists = False
        
        if index_exists:
            print(f"\n⚠️ Index '{index_name}' zaten mevcut.")
            print("   MongoDB Atlas konsolunda durumunu izleyebilirsiniz.")
        else:
            print(f"\n➕ Yeni index '{index_name}' oluşturuluyor...")
            # Raw MongoDB command ile search index oluştur
            command = {
                "createSearchIndex": {
                    "definition": index_definition,
                    "name": index_name,
                    "type": "vectorSearch"
                }
            }
            db.command(command, collection_name="taxonomy")
            print(f"✓ Index '{index_name}' başarıyla oluşturuldu.")
        
        print("\n" + "=" * 70)
        print("🎉 Vector Search index kurulumu tamamlandı!")
        print("=" * 70)
        print("\n💡 İpucu: Index senkronizasyonu birkaç dakika sürebilir.")
        print("   MongoDB Atlas konsolunda durumunu izleyebilirsiniz.")
        
    except Exception as e:
        print(f"\n❌ Index oluşturma hatası: {e}")
        print("\n💡 Eğer 'Search index not supported' hatası alıyorsanız:")
        print("   - Cluster'ınızın M10 veya daha üstü olduğundan emin olun.")
        print("   - MongoDB Atlas konsolunda 'Atlas Search' sekmesine gidin.")
        print("   - Index'i manuel olarak oluşturabilirsiniz.")
        import traceback
        traceback.print_exc()
        raise
    finally:
        client.close()
        print("\n🔌 MongoDB bağlantısı kapatıldı.")


if __name__ == "__main__":
    create_vector_search_index()
