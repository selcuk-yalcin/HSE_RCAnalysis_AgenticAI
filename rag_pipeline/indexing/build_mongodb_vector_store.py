"""
Build MongoDB Vector Store - Taxonomy'den MongoDB'ye Veri Aktarımı
===================================================================

Bu script, rag_pipeline/data/processed/taxonomy_multilingual.json dosyasını okur,
her bir 'cause' için anlamsal embedding'ler oluşturur ve bunları bir MongoDB
koleksiyonuna kaydederek bir vektör deposu oluşturur.

MongoDB Atlas'ta 'rca' adında bir database ve 'taxonomy' adında bir collection
oluşturulmalıdır. Ayrıca, 'taxonomy' collection'ı üzerinde bir vektör arama
index'i tanımlanmalıdır.

Kullanım:
    python rag_pipeline/indexing/build_mongodb_vector_store.py
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from sentence_transformers import SentenceTransformer

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rag_pipeline.schemas.cause_models import Taxonomy, Cause

# Ortam değişkenlerini yükle
load_dotenv()


class MongoVectorStoreBuilder:
    """
    Yapılandırılmış taksonomi verisinden bir MongoDB vektör deposu oluşturur.
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        print(f"🤖 Sentence Transformer modeli yükleniyor: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.taxonomy: Optional[Taxonomy] = None
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None

    def connect_to_db(self):
        """MongoDB'ye bağlanır."""
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI ortam değişkeni bulunamadı.")
        
        print("🗄️ MongoDB'ye bağlanılıyor...")
        self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        
        # Ping ile bağlantıyı test et
        try:
            self.client.admin.command('ping')
            print("✓ MongoDB bağlantısı başarılı!")
        except Exception as e:
            print(f"❌ MongoDB bağlantısı başarısız: {e}")
            raise
            
        self.db = self.client.rca
        self.collection = self.db.taxonomy

    def load_taxonomy(self, json_path: Path):
        """JSON dosyasından taksonomiyi yükler."""
        if not json_path.exists():
            raise FileNotFoundError(f"Taxonomy JSON dosyası bulunamadı: {json_path}")
        
        print(f"📚 Taxonomy JSON yükleniyor: {json_path.name}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.taxonomy = Taxonomy(**data)
        print(f"✓ {len(self.taxonomy.causes)} cause yüklendi.")

    def build_and_upload(self):
        """Ana işlem: Veriyi yükler, vektörleri oluşturur ve MongoDB'ye yükler."""
        # Taksonomi daha önce yüklenmemişse, varsayılan dosya yolundan yüklemeye çalış
        if self.taxonomy is None:
            print("📚 Taxonomy JSON yükleniyor: taxonomy_multilingual.json (varsayılan yol)")
            default_path = Path(__file__).parent.parent.parent / "rag_pipeline" / "data" / "processed" / "taxonomy_multilingual.json"
            self.load_taxonomy(default_path)
        
        if self.taxonomy is None or self.collection is None:
            print("❌ Hata: Taksonomi yüklenemedi veya veritabanı koleksiyonu bulunamadı. İşlem durduruldu.")
            return

        self.causes = self.taxonomy.causes
        if not self.causes:
            print("⚠️ Uyarı: Taksonomide 'causes' bulunamadı veya liste boş.")
            return
        
        print(f"✓ {len(self.causes)} cause yüklendi.")

        # Koleksiyonu temizle
        print("🗑️ Eski koleksiyon temizleniyor...")
        self.collection.delete_many({})
        
        print("\n✨ Vektörler oluşturuluyor ve veriler MongoDB'ye yükleniyor...")
        
        # Toplu yazdırma için liste
        documents_to_upload = []
        texts_to_embed = []
        
        for cause in self.causes:
            texts_to_embed.append(cause.to_embedding_text())
        
        embeddings = self.model.encode(texts_to_embed, convert_to_tensor=False, show_progress_bar=True)
        
        for i, cause in enumerate(self.causes):
            doc = cause.model_dump(by_alias=True)
            doc['embedding'] = embeddings[i].tolist()
            documents_to_upload.append(doc)
            
        print(f"✓ {len(documents_to_upload)} belge MongoDB'ye yüklenmeye hazır.")
        
        print("⬆️ Yeni belgeler yükleniyor...")
        self.collection.insert_many(documents_to_upload)
        
        print(f"✅ {len(documents_to_upload)} belge başarıyla MongoDB'ye yüklendi.")

    def close_connection(self):
        """MongoDB bağlantısını kapatır."""
        if self.client:
            self.client.close()
            print("\n🔌 MongoDB bağlantısı kapatıldı.")


def main():
    """Ana çalıştırma fonksiyonu."""
    print("=" * 70)
    print("🚀 MongoDB Vector Store Builder")
    print("=" * 70)
    
    # Dosya yolları
    project_root = Path(__file__).parent.parent.parent
    json_path = project_root / "rag_pipeline" / "data" / "processed" / "taxonomy_multilingual.json"
    
    builder = None
    try:
        # Builder'ı oluştur
        builder = MongoVectorStoreBuilder()
        
        # DB'ye bağlan
        builder.connect_to_db()
        
        # Taksonomiyi yükle
        builder.load_taxonomy(json_path)
        
        # Index'i oluştur ve yükle
        builder.build_and_upload()
        
        print("\n" + "=" * 70)
        print("🎉 MongoDB vektör deposu başarıyla oluşturuldu!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if builder:
            builder.close_connection()


if __name__ == "__main__":
    main()
