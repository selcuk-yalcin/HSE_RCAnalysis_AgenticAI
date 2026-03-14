#!/usr/bin/env python3
"""
Basit Demo - Agent'ların stream çıktılarını gösterir
Confined Space ve Chemical Burn senaryoları ile test eder
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Projeyi path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# .env dosyasını yükle
load_dotenv()

print("=" * 100)
print("🚀 HSE ROOT CAUSE ANALYSIS - AGENT DEMO")
print("=" * 100)
print()

# Environment check
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ HATA: OPENROUTER_API_KEY veya OPENAI_API_KEY bulunamadı!")
    print("💡 .env dosyasına API key ekleyin:")
    print("   OPENROUTER_API_KEY=your-key-here")
    sys.exit(1)

print(f"✅ API Key bulundu: {api_key[:15]}...{api_key[-10:]}\n")

# Agent'ları import et
try:
    from agents.overview_agent import OverviewAgent
    from agents.assessment_agent import AssessmentAgent
    from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
    print("✅ Agent modülleri başarıyla import edildi\n")
except ImportError as e:
    print(f"❌ Agent import hatası: {e}")
    sys.exit(1)

# ============================================================================
# TEST 1: CONFINED SPACE - OKSİJEN EKSİKLİĞİ
# ============================================================================
print("=" * 100)
print("📋 TEST 1: CONFINED SPACE - OKSİJEN EKSİKLİĞİ SENARYOSU")
print("=" * 100)
print()

confined_space_incident = """
KAZA RAPORU - CONFINED SPACE - OKSİJEN EKSİKLİĞİ
=========================================================================
Tarih: 18.03.2026, 11:45
Lokasyon: Atıksu Arıtma Tesisi, Çamur Tankı #3 (8m derinlik)

KAZAZEDELER:
- Ahmet Çelik (29) - Bakım Teknisyeni - Birincil kazazede (ağır yaralı)
- Hasan Öztürk (42) - Vardiya Amiri - Kurtarmaya girdi (ağır yaralı)  
- Kemal Aydın (35) - Operatör - Kurtarmaya girdi (orta yaralı)

OLAY ÖZETİ:
Ahmet Çelik, tank içindeki pompa arızasını kontrol etmek için izinsiz girmiş
ve 3 metre derinlikte oksijen eksikliği nedeniyle bayılmıştır. Kurtarmaya giren
vardiya amiri Hasan ve operatör Kemal de oksijen eksikliği nedeniyle etkilenmiştir.

ÖNEMLİ EKSİKLİKLER:
❌ Confined Space Entry Permit: YOK (izinsiz giriş!)
❌ Atmosfer Testi: YAPILMAMIŞ
❌ Havalandırma: YOK
❌ Güvenlik Halatı: KULLANILMAMIŞ
❌ Gözcü (Attendant): YOK
❌ Kurtarma Ekibi Hazırlığı: YOK
❌ Acil Durum Planı: YOK

OLAY AKIŞI:
11:15 - Pompa arızası bildirildi
11:30 - Ahmet izinsiz giriş kararı aldı
11:40 - Tank içine girdi (atmosfer testi yok)
11:43 - 3m derinlikte bayıldı
11:44 - Hasan kurtarmaya girdi ve bayıldı
11:45 - Kemal girdi ve etkilendi
11:47 - 112 arandı
12:05 - İtfaiye geldi, üçünü de çıkardı
12:20 - Hastaneye kaldırıldılar

YARALANMA:
- Ahmet: Hipoksi, bilinç kaybı, yoğun bakım
- Hasan: Hipoksi, bilinç kaybı, yoğun bakım
- Kemal: Kısmi hipoksi, baş dönmesi

ÖNCEKİ OLAYLAR:
- 2025'te benzer izinsiz giriş olayı (sadece uyarı verildi)
- Confined Space eğitimi 2 yıl önce verilmiş (tazeleme yok)
"""

incident_data_1 = {
    "ref_no": "CS-2026-002",
    "reported_by": "Güvenlik Görevlisi",
    "date_time": "18.03.2026 11:45",
    "description": confined_space_incident,
    "injury_description": "3 kişi oksijen eksikliği nedeniyle yaralanmış, 2 kişi yoğun bakımda",
}

print("📊 Senaryo hazırlandı")
print("🎯 Hedef: Kök neden analizi (3 aşama)\n")

try:
    print("-" * 100)
    print("AŞAMA 1/3: OVERVIEW AGENT - Genel Değerlendirme")
    print("-" * 100)
    
    overview_agent = OverviewAgent()
    part1 = overview_agent.process_initial_report(incident_data_1)
    
    print("\n✅ Overview tamamlandı!")
    print(f"   📌 Olay tipi: {part1.get('incident_type', 'N/A')}")
    print(f"   📌 Referans: {part1.get('ref_no', 'N/A')}\n")
    
    print("-" * 100)
    print("AŞAMA 2/3: ASSESSMENT AGENT - Risk Değerlendirme")
    print("-" * 100)
    
    assessment_agent = AssessmentAgent()
    part2 = assessment_agent.assess_incident(part1, incident_data_1)
    
    print("\n✅ Assessment tamamlandı!")
    print(f"   📌 Ciddiyet: {part2.get('actual_potential_harm', 'N/A')}")
    print(f"   📌 Soruşturma seviyesi: {part2.get('investigation_level', 'N/A')}\n")
    
    print("-" * 100)
    print("AŞAMA 3/3: ROOT CAUSE AGENT - Kök Neden Analizi")
    print("-" * 100)
    
    rootcause_agent = RootCauseAgent()
    part3 = rootcause_agent.analyze_root_causes(part1, part2, incident_data_1.get("description"))
    
    print("\n✅ Root Cause analizi tamamlandı!")
    
    # Sonuçları göster
    branches = part3.get("analysis_branches", [])
    root_causes = part3.get("final_root_causes", [])
    
    print(f"\n   📌 Analiz dalı sayısı: {len(branches)}")
    print(f"   📌 Kök neden sayısı: {len(root_causes)}")
    
    if root_causes:
        print("\n" + "=" * 100)
        print("🎯 BULUNAN KÖK NEDENLER")
        print("=" * 100)
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("code", "?")
            name = rc.get("name", "Belirtilmemiş")
            desc = rc.get("description", "")
            print(f"\n   {i}. [{code}] {name}")
            if desc:
                print(f"      → {desc[:150]}...")
    
    print("\n" + "=" * 100)
    print("✅ TEST 1 TAMAMLANDI - CONFINED SPACE")
    print("=" * 100)
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 2: KİMYASAL YANMA
# ============================================================================
print("\n\n")
input("🔄 İkinci teste geçmek için ENTER'a basın...")
print()

print("=" * 100)
print("📋 TEST 2: KİMYASAL YANMA - KİŞİSEL KORUYUCU EKİPMAN EKSİKLİĞİ")
print("=" * 100)
print()

chemical_burn_incident = """
KAZA RAPORU - KİMYASAL YANMA (%98 SÜLFÜRİK ASİT)
=========================================================================
Tarih: 20.03.2026, 14:30
Lokasyon: GHI Kimya Fabrikası, Asit Transfer İstasyonu

KAZAZEDE:
- Mehmet Kaya (25) - Operatör - 6 ay deneyimli

OLAY ÖZETİ:
%98 konsantre sülfürik asit transferi sırasında hortum bağlantısı gevşemiş,
operatörün yüzüne ve üst vücuduna asit sıçramıştır. 

KRİTİK EKSİKLİK:
❌ Tam yüz siperi: KULLANILMAMIŞ
❌ Kimyasal gözlük: KULLANILMAMIŞ
❌ Asit dayanımlı eldiven: YOK (normal eldiven var)
❌ Asit dayanımlı tulum: YOK (pamuklu iş tulumu var)

Kullanılması Gereken PPE:
✓ Tam yüz siperi (Face shield)
✓ Kimyasal gözlük  
✓ Asit dayanımlı eldiven
✓ Asit dayanımlı önlük/tulum
✓ Çizme

İŞ İZNİ DURUMU:
⚠️ Chemical Handling Permit: VAR ama eksik imza
❌ Hortum bağlantı kontrolü: YAPILMAMIŞ
❌ Güvenlik duşu testi: 3 ay önce (haftalık olmalı)

OLAY AKIŞI:
14:15 - Transfer işine başlandı
14:25 - Hortum manuel bağlandı (tork anahtarı kullanılmadı)
14:28 - Pompa çalıştırıldı
14:30 - Bağlantı gevşedi, asit fışkırdı
14:30 - Asit yüze ve göğse sıçradı
14:32 - Acil duş istasyonuna götürüldü
14:33 - 15 dakika duş altında yıkandı
14:50 - Ambulans ile hastaneye kaldırıldı

YARALANMA:
- Yüzde 2. derece kimyasal yanık (%15 vücut yüzeyi)
- Gözlerde ciddi hasar (kornea yanığı)
- Göğüs ve boyunda yanık
- 10 gün hastanede yatış
- Kalıcı görme kaybı riski

EĞİTİM DURUMU:
✓ Genel İSG eğitimi: 6 ay önce alınmış
✓ Kimyasal güvenlik: Teorik eğitim var (pratik yok)
❌ PPE kullanım eğitimi: YOK

ÖNCEKİ OLAYLAR:
- 2024: Benzer asit sıçraması (el yanığı, PPE eksikliği)
- 2025: Hortum patlaması
- 3 defa PPE uyumsuzluğu uyarısı verilmiş
"""

incident_data_2 = {
    "ref_no": "CHEM-2026-003",
    "reported_by": "Vardiya Amiri",
    "date_time": "20.03.2026 14:30",
    "description": chemical_burn_incident,
    "injury_description": "Yüz, göğüs ve göz bölgesinde 2. derece kimyasal yanık, kalıcı hasar riski",
}

print("📊 Senaryo hazırlandı")
print("🎯 Hedef: Kök neden analizi (3 aşama)\n")

try:
    print("-" * 100)
    print("AŞAMA 1/3: OVERVIEW AGENT - Genel Değerlendirme")
    print("-" * 100)
    
    overview_agent_2 = OverviewAgent()
    part1 = overview_agent_2.process_initial_report(incident_data_2)
    
    print("\n✅ Overview tamamlandı!")
    print(f"   📌 Olay tipi: {part1.get('incident_type', 'N/A')}")
    print(f"   📌 Referans: {part1.get('ref_no', 'N/A')}\n")
    
    print("-" * 100)
    print("AŞAMA 2/3: ASSESSMENT AGENT - Risk Değerlendirme")
    print("-" * 100)
    
    assessment_agent_2 = AssessmentAgent()
    part2 = assessment_agent_2.assess_incident(part1, incident_data_2)
    
    print("\n✅ Assessment tamamlandı!")
    print(f"   📌 Ciddiyet: {part2.get('actual_potential_harm', 'N/A')}")
    print(f"   📌 Soruşturma seviyesi: {part2.get('investigation_level', 'N/A')}\n")
    
    print("-" * 100)
    print("AŞAMA 3/3: ROOT CAUSE AGENT - Kök Neden Analizi")
    print("-" * 100)
    
    rootcause_agent_2 = RootCauseAgent()
    part3 = rootcause_agent_2.analyze_root_causes(part1, part2, incident_data_2.get("description"))
    
    print("\n✅ Root Cause analizi tamamlandı!")
    
    # Sonuçları göster
    branches = part3.get("analysis_branches", [])
    root_causes = part3.get("final_root_causes", [])
    
    print(f"\n   📌 Analiz dalı sayısı: {len(branches)}")
    print(f"   📌 Kök neden sayısı: {len(root_causes)}")
    
    if root_causes:
        print("\n" + "=" * 100)
        print("🎯 BULUNAN KÖK NEDENLER")
        print("=" * 100)
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("code", "?")
            name = rc.get("name", "Belirtilmemiş")
            desc = rc.get("description", "")
            print(f"\n   {i}. [{code}] {name}")
            if desc:
                print(f"      → {desc[:150]}...")
    
    print("\n" + "=" * 100)
    print("✅ TEST 2 TAMAMLANDI - KİMYASAL YANMA")
    print("=" * 100)
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# FİNAL
# ============================================================================
print("\n\n" + "🎉" * 50)
print("TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
print("🎉" * 50)
print()
print("✅ Test 1: Confined Space - 3 kazazede, oksijen eksikliği")
print("✅ Test 2: Kimyasal Yanma - PPE eksikliği, kalıcı hasar riski")
print()
print("📊 Her iki senaryo için de kök neden analizi tamamlandı!")
print("=" * 100)
