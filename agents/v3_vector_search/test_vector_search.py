"""
V3 Vector Search Test Script
=============================
MongoDB Vector Search + RootCauseAgentV3 test uygulaması

KULLANIM:
python agents/v3_vector_search/test_vector_search.py
"""

import sys
import os

# V3 klasörünü path'e ekle
v3_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(v3_dir)
if v3_dir not in sys.path:
    sys.path.insert(0, v3_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from dotenv import load_dotenv
load_dotenv()

# Test senaryosu
INCIDENT_DESCRIPTION = """
Tarih: 15 Ocak 2024
Lokasyon: Rafineri ünitesi, yüksek basınç tesisatı bakım alanı

OLAY:
Bakım teknisyeni Ali, yüksek basınç tesisatında sızıntı kontrolü yaparken,
sistemi izole etmeden (LOTO prosedürü uygulamadan) vananın altındaki
flanşı gevşetmeye başladı. Sistem hala basınçlı olduğu için, flanj çözüldüğünde
ani basınç boşalması meydana geldi ve kimyasal sıvı fışkırdı. 

Ali, bu işlemi daha önce "hızlı iş" olarak 4-5 kez yapmıştı ve hiç sorun
çıkmamıştı. Vardiya amiri, sahada bulunmuyordu ve bu tip kestirme yöntemlerin
kullanıldığından habersizdi.

Şirketin LOTO prosedürü yazılı olarak mevcuttu ancak son 1 yılda hiç denetim
yapılmamıştı. Bakım ekibi, prosedürlerin "fazla zaman aldığını" düşünüyor
ve rutin işlerde atlamayı normal karşılıyordu.

SONUÇ:
Ali'nin yüzüne ve vücuduna kimyasal sıçradı. İkinci derece yanık ve göz 
tahriş yaralanması. 2 hafta iş göremez durumda.
"""


def test_vector_search_only():
    """Sadece vector search yeteneklerini test et"""
    print("\n" + "=" * 80)
    print("🧪 TEST 1: Vector Search Yetenekleri")
    print("=" * 80)
    
    try:
        from knowledge_base_vector_v3 import HSG245VectorDB
        
        db = HSG245VectorDB()
        
        # Test query
        query = "Worker bypassed LOTO procedure, repeated violation, no supervision"
        
        print(f"\n🔍 Query: {query}\n")
        
        # D kategorisi (organizational)
        print("📁 D KATEGORİSİ (ORGANİZASYONEL ROOT CAUSES):")
        print("-" * 80)
        
        results_d = db.semantic_search(query, top_k=5, category_filter="D")
        
        if results_d:
            for i, r in enumerate(results_d, 1):
                print(f"\n{i}. {r['code']} (Score: {r['score']:.3f})")
                print(f"   {r['title']}")
                if r.get('typical_examples'):
                    print(f"   Örnek: {r['typical_examples'][0][:150]}...")
        else:
            print("⚠️  Sonuç bulunamadı (Vector index oluşturulmamış olabilir)")
        
        # C kategorisi (personal)
        print("\n\n📁 C KATEGORİSİ (KİŞİSEL ROOT CAUSES):")
        print("-" * 80)
        
        results_c = db.semantic_search(query, top_k=3, category_filter="C")
        
        if results_c:
            for i, r in enumerate(results_c, 1):
                print(f"\n{i}. {r['code']} (Score: {r['score']:.3f})")
                print(f"   {r['title']}")
                if r.get('typical_examples'):
                    print(f"   Örnek: {r['typical_examples'][0][:150]}...")
        else:
            print("⚠️  Sonuç bulunamadı")
        
        print("\n✅ Vector search testi tamamlandı")
        return True
        
    except Exception as e:
        print(f"\n❌ Vector search testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_kb():
    """Hibrit knowledge base'i test et"""
    print("\n" + "=" * 80)
    print("🧪 TEST 2: Hibrit Knowledge Base")
    print("=" * 80)
    
    try:
        from knowledge_base_vector_v3 import HybridKnowledgeBase
        
        kb = HybridKnowledgeBase()
        
        print("\n📋 Test incident özeti:")
        print(INCIDENT_DESCRIPTION[:200] + "...")
        
        print("\n\n🔍 D Kategorisi için ilgili kodlar getiriliyor...")
        print("-" * 80)
        
        context_d = kb.get_relevant_codes(
            incident_summary=INCIDENT_DESCRIPTION,
            category="D",
            top_k=5
        )
        
        # İlk 1000 karakteri göster
        print(context_d[:1000])
        print(f"\n... (Toplam {len(context_d)} karakter)\n")
        
        print("✅ Hibrit KB testi tamamlandı")
        return True
        
    except Exception as e:
        print(f"\n❌ Hibrit KB testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rootcause_v3():
    """RootCauseAgentV3 ile tam analiz"""
    print("\n" + "=" * 80)
    print("🧪 TEST 3: RootCauseAgentV3 - Tam Analiz")
    print("=" * 80)
    
    try:
        from rootcause_agent_v3 import RootCauseAgentV3
        
        # Agent'ı başlat
        agent = RootCauseAgentV3()
        
        # Dummy part1 ve part2 data
        part1_data = {
            "description": INCIDENT_DESCRIPTION,
            "incident_type": "Chemical Exposure",
            "date": "15 Ocak 2024"
        }
        
        part2_data = {
            "event_type": "Occupational Injury",
            "severity": "Serious"
        }
        
        investigation_data = {
            "description": INCIDENT_DESCRIPTION
        }
        
        print("\n🚀 Analiz başlatılıyor...\n")
        
        # Analiz
        result = agent.analyze_root_causes(
            part1_data=part1_data,
            part2_data=part2_data,
            investigation_data=investigation_data
        )
        
        # Rapor
        print("\n\n" + "=" * 80)
        print("📊 ANALİZ RAPORU")
        print("=" * 80)
        print(result.get("final_report_tr", "Rapor oluşturulamadı"))
        
        # Root causes özeti
        print("\n\n" + "=" * 80)
        print("🎯 ROOT CAUSES ÖZETİ")
        print("=" * 80)
        
        for i, rc in enumerate(result.get("final_root_causes", []), 1):
            code = rc.get('code', '???')
            title = rc.get('standard_title_tr', '')
            cause = rc.get('cause_tr', '')
            
            print(f"\n{i}. [{code}] {title}")
            print(f"   {cause}")
        
        print("\n✅ RootCauseAgentV3 testi tamamlandı")
        return True
        
    except Exception as e:
        print(f"\n❌ RootCauseAgentV3 testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ana test runner"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "V3 VECTOR SEARCH TEST SÜİTİ" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Environment kontrolü
    print("\n🔧 Environment Kontrolü:")
    print("-" * 80)
    
    use_vector = os.getenv("USE_VECTOR_SEARCH", "false").lower() == "true"
    mongo_uri = os.getenv("MONGODB_URI")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    print(f"USE_VECTOR_SEARCH: {use_vector}")
    print(f"MONGODB_URI: {'✅ Ayarlanmış' if mongo_uri else '❌ Eksik'}")
    print(f"OPENROUTER_API_KEY: {'✅ Ayarlanmış' if openrouter_key else '❌ Eksik'}")
    
    if not use_vector:
        print("\n⚠️  USE_VECTOR_SEARCH=false - Dictionary modu aktif")
        print("   Vector search testlerini atlamak için Enter'a basın...")
        print("   Vector search'ü aktif etmek için .env'de USE_VECTOR_SEARCH=true yapın")
        input()
    
    if use_vector and (not mongo_uri or not openrouter_key):
        print("\n❌ Vector search için gerekli environment variables eksik!")
        print("   .env dosyasına şunları ekleyin:")
        print("   MONGODB_URI=mongodb+srv://...")
        print("   OPENROUTER_API_KEY=sk-or-v1-...")
        return
    
    # Testleri çalıştır
    results = []
    
    # Test 1: Vector search (sadece USE_VECTOR_SEARCH=true ise)
    if use_vector:
        results.append(("Vector Search", test_vector_search_only()))
        
        # Test 2: Hibrit KB
        results.append(("Hibrit KB", test_hybrid_kb()))
    else:
        print("\n⏭️  Vector search testleri atlandı (USE_VECTOR_SEARCH=false)")
    
    # Test 3: RootCauseAgentV3 (her zaman)
    results.append(("RootCauseAgentV3", test_rootcause_v3()))
    
    # Özet
    print("\n\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 30 + "TEST ÖZETİ" + " " * 38 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    for test_name, passed in results:
        status = "✅ BAŞARILI" if passed else "❌ BAŞARISIZ"
        print(f"{test_name:30} {status}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print(f"\n📊 Toplam: {passed_count}/{total} test başarılı")
    
    if passed_count == total:
        print("\n🎉 Tüm testler başarılı! V3 kullanıma hazır.")
    else:
        print("\n⚠️  Bazı testler başarısız. Lütfen hataları kontrol edin.")


if __name__ == "__main__":
    main()
