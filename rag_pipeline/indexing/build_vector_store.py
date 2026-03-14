"""
Build Vector Store - Taxonomy'den FAISS Index Oluşturucu
=========================================================

Bu script, rag_pipeline/data/processed/taxonomy_multilingual.json dosyasını okur,
her bir 'cause' için anlamsal embedding'ler oluşturur ve bunları bir FAISS
index'ine kaydederek bir vektör deposu oluşturur.

Kullanım:
    python rag_pipeline/indexing/build_vector_store.py
"""

import sys
import json
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rag_pipeline.schemas.cause_models import Taxonomy


class VectorStoreBuilder:
    """
    Yapılandırılmış taksonomi verisinden bir FAISS vektör deposu oluşturur.
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        print(f"🤖 Sentence Transformer modeli yükleniyor: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.taxonomy: Optional[Taxonomy] = None
        self.documents: List[str] = []
        self.index_to_code: Dict[int, str] = {}

    def load_taxonomy(self, json_path: Path):
        """JSON dosyasından taksonomiyi yükler."""
        if not json_path.exists():
            raise FileNotFoundError(f"Taxonomy JSON dosyası bulunamadı: {json_path}")
        
        print(f"📚 Taxonomy JSON yükleniyor: {json_path.name}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.taxonomy = Taxonomy(**data)
        print(f"✓ {len(self.taxonomy.causes)} cause yüklendi.")

    def prepare_documents(self):
        """Embedding için belgeleri (metin bloklarını) hazırlar."""
        if not self.taxonomy:
            raise ValueError("Önce taksonomi yüklenmelidir.")
            
        print("📝 Embedding için metin blokları hazırlanıyor...")
        for i, cause in enumerate(self.taxonomy.causes):
            # Her cause için zengin metin oluştur
            doc_text = cause.to_embedding_text()
            self.documents.append(doc_text)
            self.index_to_code[i] = cause.code
        
        print(f"✓ {len(self.documents)} adet metin bloğu oluşturuldu.")

    def build_index(self):
        """Metin bloklarından embedding'ler oluşturur ve FAISS index'i kurar."""
        if not self.documents:
            raise ValueError("Önce belgeler hazırlanmalıdır.")
            
        print("\n🔄 Vektör embedding'leri oluşturuluyor... (Bu işlem biraz sürebilir)")
        embeddings = self.model.encode(self.documents, convert_to_tensor=False, show_progress_bar=True)
        
        # Embedding boyutunu al
        d = embeddings.shape[1]
        print(f"✓ Embedding'ler oluşturuldu. Boyut: {d}")
        
        print("🗂️ FAISS index'i oluşturuluyor...")
        # Basit bir L2 (Euclidean) distance index'i
        index = faiss.IndexFlatL2(d)
        index.add(np.array(embeddings))
        
        print(f"✓ FAISS index'i oluşturuldu. Toplam {index.ntotal} vektör eklendi.")
        return index

    def save_all(self, index: faiss.Index, output_dir: Path):
        """FAISS index'ini ve index-code haritasını kaydeder."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # FAISS index'ini kaydet
        index_path = output_dir / "taxonomy.index"
        faiss.write_index(index, str(index_path))
        print(f"\n✅ FAISS index'i kaydedildi: {index_path}")
        
        # Index-to-code haritasını kaydet
        map_path = output_dir / "index_to_code.json"
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(self.index_to_code, f, ensure_ascii=False, indent=2)
        print(f"✅ Index-to-code haritası kaydedildi: {map_path}")


def main():
    """Ana çalıştırma fonksiyonu."""
    print("=" * 70)
    print("🚀 Vector Store Builder - FAISS Index Oluşturucu")
    print("=" * 70)
    
    # Dosya yolları
    project_root = Path(__file__).parent.parent.parent
    json_path = project_root / "rag_pipeline" / "data" / "processed" / "taxonomy_multilingual.json"
    output_dir = project_root / "rag_pipeline" / "data" / "vector_store"
    
    try:
        # Builder'ı oluştur
        builder = VectorStoreBuilder()
        
        # Taksonomiyi yükle ve belgeleri hazırla
        builder.load_taxonomy(json_path)
        builder.prepare_documents()
        
        # Index'i oluştur
        index = builder.build_index()
        
        # Her şeyi kaydet
        builder.save_all(index, output_dir)
        
        print("\n" + "=" * 70)
        print("🎉 Vektör deposu başarıyla oluşturuldu!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
