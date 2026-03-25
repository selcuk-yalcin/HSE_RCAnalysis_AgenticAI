"""
Stream Test Runner - Test senaryolarını canlı stream ile çalıştırır
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent


def print_section(title, width=100):
    """Bölüm başlığı yazdır"""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def run_confined_space_test():
    """Confined Space test senaryosu - STREAM AÇIK"""
    print_section("🚨 TEST 1: CONFINED SPACE - OKSİJEN EKSİKLİĞİ")
    
    incident_summary = """
KAZA RAPORU - CONFINED SPACE - OKSİJEN EKSİKLİĞİ
===============================================================

1. GENEL BİLGİLER
-----------------
Rapor No: CS-2026-002-OXYGEN
Tarih/Saat: 18.03.2026 / 11:45
Lokasyon: DEF Atıksu Arıtma Tesisi, Çamur Depolama Tankı #3 (5m çap, 8m derinlik)
Kazazede 1: Ahmet Çelik, 29 yaş, Bakım Teknisyeni (birincil)
Kazazede 2: Hasan Öztürk, 42 yaş, Vardiya Amiri (kurtarmaya girdi)
Kazazede 3: Kemal Aydın, 35 yaş, Operatör (kurtarmaya girdi)
Şirket: DEF Çevre Teknolojileri A.Ş.

2. OLAY ÖZETİ
-------------
Bakım teknisyeni Ahmet Çelik, tank içinde pompa arızasını kontrol etmek için izinsiz 
girmiş ve ~3 metre derinlikte bayılmıştır. Kurtarmaya giren vardiya amiri Hasan Öztürk 
da oksijen eksikliği nedeniyle bayılmış, ardından operatör Kemal Aydın da etkilenmiştir.

3. İZİN VE KONTROLLER
---------------------
- Confined Space Entry Permit: YOK (izinsiz giriş!)
- Atmosfer Testi: YAPILMAMIŞ
- Havalandırma: YOK
- Güvenlik Halatı/Emniyet Kemeri: KULLANILMAMIŞ
- Gözcü (Attendant): YOK
- Kurtarma Ekibi Hazırlığı: YOK
- Acil Durum Planı: YOK

4. OLAY GELİŞİMİ
----------------
11:15 - Vardiya başlangıcı, tank içi pompa arızası bildirildi
11:30 - Ahmet Çelik izin almadan tank içine girmeye karar verdi
11:40 - Ahmet tank içine girdi, atmosfer testi yapmadı
11:43 - Ahmet ~3m derinlikte sesini çıkarmadan yere yığıldı
11:44 - Vardiya amiri Hasan durumu gördü, kurtarmak için içeri atladı
11:45 - Hasan da bayıldı, operatör Kemal de içeri girdi ve etkilendi
11:47 - Güvenlik görevlisi alarm verdi, 112 arandı
12:05 - İtfaiye ekibi geldi, oksijen maskeli girerek kazazedeleri çıkardı
12:20 - Üç kişi de hastaneye kaldırıldı

5. YARALANMA DURUMU
-------------------
- Ahmet Çelik: Hipoksi (oksijen eksikliği), bilinç kaybı, yoğun bakım
- Hasan Öztürk: Hipoksi, bilinç kaybı, yoğun bakım
- Kemal Aydın: Kısmi hipoksi, baş dönmesi, gözlem altında

6. ÖNCEKİ OLAYLAR
-----------------
- 2025'te benzer bir tankta atmosfer testi yapılmadan giriş (uyarı ile sonuçlandı)
- Çalışanlara Confined Space eğitimi verilmiş ama 2 yıl önce (tazeleme yok)

7. HASAR/KAYIP
--------------
- İş günü kaybı: 3 çalışan (toplam ~90 gün tahmini)
- Tedavi maliyeti: Yüksek (3 yoğun bakım)
- Operasyon durması: Tank bakımı 2 gün ertelendi
- İtibar kaybı: Yerel medyada haber oldu
"""

    print("📋 Olay özeti hazırlandı")
    print("\n🔍 ADIM 1: OVERVIEW AGENT - Genel değerlendirme başlıyor...\n")
    print("-" * 100)
    
    overview_agent = OverviewAgent()
    overview_result = overview_agent.run(incident_summary, stream=True)  # STREAM AÇIK
    
    print("\n" + "-" * 100)
    print("\n✅ Overview tamamlandı!")
    print(f"📊 Olay tipi: {overview_result.get('incident_type', 'N/A')}")
    print(f"⚠️  Kaza sınıfı: {overview_result.get('accident_class', 'N/A')}")
    
    print("\n\n🔍 ADIM 2: ASSESSMENT AGENT - Detaylı analiz başlıyor...\n")
    print("-" * 100)
    
    assessment_agent = AssessmentAgent()
    assessment_result = assessment_agent.run(incident_summary, overview_result, stream=True)  # STREAM AÇIK
    
    print("\n" + "-" * 100)
    print("\n✅ Assessment tamamlandı!")
    print(f"📌 Tehlike kaynağı sayısı: {len(assessment_result.get('hazard_sources', []))}")
    
    print("\n\n🔍 ADIM 3: ROOT CAUSE AGENT - Kök neden analizi başlıyor...\n")
    print("-" * 100)
    
    rootcause_agent = RootCauseAgent()
    rootcause_result = rootcause_agent.run(
        incident_summary, 
        overview_result, 
        assessment_result, 
        stream=True  # STREAM AÇIK
    )
    
    print("\n" + "-" * 100)
    print("\n✅ Root Cause analizi tamamlandı!")
    
    print_section("📊 CONFINED SPACE TESTİ TAMAMLANDI", 100)
    print(f"✓ Overview: {len(overview_result)} anahtar")
    print(f"✓ Assessment: {len(assessment_result)} anahtar")
    print(f"✓ Root Cause: {len(rootcause_result)} anahtar")
    
    return {
        'overview': overview_result,
        'assessment': assessment_result,
        'rootcause': rootcause_result
    }


def run_chemical_test():
    """Chemical Burn test senaryosu - STREAM AÇIK"""
    print_section("🚨 TEST 2: KİMYASAL YANMA - KİŞİSEL KORUYUCU EKİPMAN EKSİKLİĞİ")
    
    incident_summary = """
KAZA RAPORU - KİMYASAL YANMA
===============================================================

1. GENEL BİLGİLER
-----------------
Rapor No: CHEM-2026-003-BURN
Tarih/Saat: 20.03.2026 / 14:30
Lokasyon: GHI Kimya Fabrikası, Asit Transfer İstasyonu
Kazazede: Mehmet Kaya, 25 yaş, Operatör (6 ay deneyim)
Şirket: GHI Kimya Sanayi A.Ş.

2. OLAY ÖZETİ
-------------
Konsantre sülfürik asit (%98) transferi sırasında hortum bağlantısı gevşemiş, 
operatör Mehmet Kaya'nın yüzüne ve üst vücuduna asit sıçramıştır. 
Kimyasal koruyucu gözlük ve yüz siperi kullanılmamıştır.

3. KİŞİSEL KORUYUCU EKİPMAN
---------------------------
Olması Gereken:
- Tam yüz siperi (Face shield)
- Kimyasal gözlük
- Asit dayanımlı eldiven
- Asit dayanımlı önlük/tulum
- Çizme

Kullanılan:
- Sadece pamuklu iş tulumu (asit dayanımlı DEĞİL!)
- Normal iş eldiveni (kimyasal koruma YOK!)
- Gözlük/yüz siperi: KULLANILMAMIŞ

4. İŞ İZNİ VE KONTROLLER
-----------------------
- Hot Work Permit: YOK (gerekli değil)
- Chemical Handling Permit: VAR ama eksik imza
- Hortum bağlantı kontrolü: YAPILMAMIŞ
- Güvenlik duşu testi: 3 ay önce yapılmış (haftalık olmalı)
- Göz yıkama istasyonu: Çalışıyor
- Risk değerlendirmesi: 1 yıl önce (güncel değil)

5. OLAY GELİŞİMİ
----------------
14:15 - Sülfürik asit transfer işine başlandı
14:25 - Hortum bağlantısı manuel olarak yapıldı (tork anahtarı kullanılmadı)
14:28 - Transfer pompası çalıştırıldı
14:30 - Bağlantı noktası gevşedi, asit fışkırdı
14:30 - Asit operatörün yüzüne ve göğsüne sıçradı
14:31 - Operatör acı ile bağırdı, gözleri yanmaya başladı
14:32 - İş arkadaşı acil duş istasyonuna götürdü
14:33 - 15 dakika boyunca duş altında yıkandı
14:50 - Ambulans geldi, hastaneye kaldırıldı

6. YARALANMA DURUMU
-------------------
- Yüzde 2. derece kimyasal yanık (%15 vücut yüzeyi)
- Gözlerde ciddi hasar (kornea yanığı)
- Göğüs ve boyunda yanık
- Hastanede 10 gün yatış
- Kalıcı görme kaybı riski var

7. ÖNCEKİ OLAYLAR
-----------------
- 2024'te benzer asit sıçraması (el yanığı, PPE eksikliği)
- 2025'te hortum patlaması (farklı lokasyon)
- PPE uyumsuzluğu nedeniyle 3 defa uyarı verilmiş

8. EĞİTİM DURUMU
----------------
- Genel İSG eğitimi: Alınmış (6 ay önce, işe girişte)
- Kimyasal güvenlik eğitimi: Alınmış ama teorik (pratik yok)
- Acil durum eğitimi: 1 yıl önce
- PPE kullanım eğitimi: YOK
"""

    print("📋 Olay özeti hazırlandı")
    print("\n🔍 ADIM 1: OVERVIEW AGENT - Genel değerlendirme başlıyor...\n")
    print("-" * 100)
    
    overview_agent = OverviewAgent()
    overview_result = overview_agent.run(incident_summary, stream=True)  # STREAM AÇIK
    
    print("\n" + "-" * 100)
    print("\n✅ Overview tamamlandı!")
    print(f"📊 Olay tipi: {overview_result.get('incident_type', 'N/A')}")
    print(f"⚠️  Kaza sınıfı: {overview_result.get('accident_class', 'N/A')}")
    
    print("\n\n🔍 ADIM 2: ASSESSMENT AGENT - Detaylı analiz başlıyor...\n")
    print("-" * 100)
    
    assessment_agent = AssessmentAgent()
    assessment_result = assessment_agent.run(incident_summary, overview_result, stream=True)  # STREAM AÇIK
    
    print("\n" + "-" * 100)
    print("\n✅ Assessment tamamlandı!")
    print(f"📌 Tehlike kaynağı sayısı: {len(assessment_result.get('hazard_sources', []))}")
    
    print("\n\n🔍 ADIM 3: ROOT CAUSE AGENT - Kök neden analizi başlıyor...\n")
    print("-" * 100)
    
    rootcause_agent = RootCauseAgent()
    rootcause_result = rootcause_agent.run(
        incident_summary, 
        overview_result, 
        assessment_result, 
        stream=True  # STREAM AÇIK
    )
    
    print("\n" + "-" * 100)
    print("\n✅ Root Cause analizi tamamlandı!")
    
    print_section("📊 CHEMICAL BURN TESTİ TAMAMLANDI", 100)
    print(f"✓ Overview: {len(overview_result)} anahtar")
    print(f"✓ Assessment: {len(assessment_result)} anahtar")
    print(f"✓ Root Cause: {len(rootcause_result)} anahtar")
    
    return {
        'overview': overview_result,
        'assessment': assessment_result,
        'rootcause': rootcause_result
    }


if __name__ == "__main__":
    import sys
    
    print("\n" + "🎯" * 50)
    print("STREAM TEST RUNNER - 2 SENARYO")
    print("🎯" * 50 + "\n")
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "confined":
            run_confined_space_test()
        elif test_name == "chemical":
            run_chemical_test()
        else:
            print("❌ Geçersiz test adı! Kullanım:")
            print("   python run_stream_test.py confined")
            print("   python run_stream_test.py chemical")
    else:
        # İki testi de çalıştır
        print("🔥 Her iki test de çalıştırılacak...\n")
        
        try:
            result1 = run_confined_space_test()
            print("\n\n⏸️  İlk test tamamlandı, ikinci teste geçiliyor...\n")
            input("Enter'a basarak devam edin...")
            
            result2 = run_chemical_test()
            
            print("\n" + "🎉" * 50)
            print("TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
            print("🎉" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⛔ Test kullanıcı tarafından durduruldu!")
        except Exception as e:
            print(f"\n\n❌ HATA: {str(e)}")
            import traceback
            traceback.print_exc()
