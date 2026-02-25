#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: KMCO LLC - İzobütilen Patlaması, Yangın ve Ölüm Olayı
Tesis: KMCO LLC, Crosby, Texas
Olay: Y-filtre arızası → izobütilen buhar bulutu → patlama ve yangın
Tarih: 2 Nisan 2019, Saat: 10:51
Sonuç: 1 ölü (Pano Operatörü 2), 2 ağır yaralı, 28 yaralı
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from shared.config import Config

def print_header(title, char="=", width=80):
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")

def print_step(step_num, title):
    print_header(f"ADIM {step_num}: {title}")

def print_success(message):
    print(f"  ✅ {message}")

def print_info(message):
    print(f"  {message}")

# ============================================================================
# KMCO LLC - İZOBÜTİLEN PATLAMASI, YANGIN VE ÖLÜM OLAYI
# ============================================================================
INCIDENT_DESCRIPTION = """
OLAY RAPORU - PATLAMA, YANGIN VE ÖLÜM

Tarih: 2 Nisan 2019, Saat: 10:51
Lokasyon: KMCO LLC Tesisi, Crosby, Texas, ABD
İşletmeci: KMCO LLC
Etkilenen Ekipman: 3 inç dökme demir Y-filtre (Y-strainer), izobütilen besleme hattı
Rapor Eden: CSB (Kimyasal Güvenlik Kurulu)
Olay Sonucu: 1 çalışan hayatını kaybetti, 2 çalışan ağır yaralandı, toplam 28 kişi yaralandı

OLAY ÖZETİ:
2 Nisan 2019 sabahı KMCO tesisinde kükürtlü izobütilen (sülfürize izobütilen) üretimi için
parti hazırlanıyordu. Saat 10:41'de besleme pompasının emme hattındaki 3 inçlik gri dökme
demir Y-filtre gövdesinden yumruk büyüklüğünde bir metal parça koptu. Bu kopma sonucu
yaklaşık 4.500 kg sıvı izobütilen atmosfere salındı ve yanıcı buhar bulutu oluştu. Saat
10:51'de buhar bulutu tutuşarak patladı. Patlama anında Pano Operatörü 2, R2 Binası
girişindeydi ve hayatını kaybetti. Pano Operatörü 1 ve Vardiya Amiri ağır yanık
yaralanmalarıyla hastaneye kaldırıldı. Tesis yakınındaki yaklaşık 1,6 km yarıçapındaki
yerleşim alanları için "yerinde kal" (shelter-in-place) emri verildi.

OLAY TİPİ: Proses Güvenliği - Yanıcı Madde Salınımı, Patlama ve Yangın

KRİTİK FAKTÖRLER:

1. EKİPMAN ARIZA VE MALZEME UYGUNSUZLUĞU:
   - Y-filtre gövdesi gri dökme demir malzemeden üretilmişti
   - Dökme demir, LPG grubu yanıcı sıvılar için uygun malzeme DEĞİLDİR
     (NFPA 58 standardı 1931'den beri LPG sistemlerinde dökme demiri yasaklamaktadır)
   - Metalurjik testler: Y-filtre iç basınç nedeniyle "gevrek kopma (brittle overload fracture)"
     sonucu parçalandı - kırılmadan önce hiçbir uyarı işareti vermedi
   - Aynı bölgede 10 Aralık 2015'te başka bir Y-filtre çatlamış, fakat filtre birebir
     değiştirilmiş, kök neden araştırılmamış ve kalıcı önlem alınmamıştı
   - Y-filtrenin proses çizimlerinde "SS" (paslanmaz çelik) olarak gösterilmesi nedeniyle
     PHA ekipleri filtrenin paslanmaz olduğunu yanlış varsaydı; gerçekte dökme demirdi
   - Filtre seçimi belgesiz ve rastlantısaldı; neden bu filtrenin kullanıldığına dair resmi kayıt
     mevcut değildi (CSB resmi kayıt bulamamıştır)

2. YÜKSEK BASINÇ OLUŞUMU - SIVI TERMAL GENLEŞMESİ:
   - Besleme pompası hattında basınç ölçümü YAPILMIYORDU
   - 2 Nisan sabahı izobütilen 13°C'de yüklendi, hava sıcaklığı 4°C'den 15°C'ye yükseldi
   - Güneş gören borularda ısınan sıvının termal genleşmesi iç basıncı artırdı
   - API 521 standardı kapalı sistemlerde termal genleşme için basınç tahliye cihazı kurulmasını
     önerir; bu gereklilik karşılanmamıştı
   - Önceki benzer yüklemelerde de yüksek basınç oluşmuş olması muhtemeldir;
     tekrarlayan termal genleşmeler Y-filtre gövdesinde mikro çatlaklara yol açmış olabilir

3. UZAKTAN İZOLASYON EKSİKLİĞİ:
   - Sistemdeki aktüatörlü (motorlu) vanaların büyük çoğunluğu YALNIZCA sahada manuel
     olarak çalıştırılabiliyordu
   - Sadece bir adet basınç kontrol vanası kontrol odasından uzaktan kontrol edilebiliyordu
   - 2010 yılında sigorta raporunda "izobütilen gibi yanıcı sıvılar içeren sistemlere yangına
     dayanıklı uzaktan kumandalı izolasyon vanaları (ROEIV) kurulması" önerildi
   - Aynı tavsiye 2017 ve 2018 sigorta değerlendirme raporlarında tekrarlandı
   - KMCO bu uyarılara rağmen izobütilen sistemine uzaktan izolasyon sağlamadı
   - Acil durumda operatörler tehlikeli alana fiziksel müdahaleye zorlandı
   - Uzaktan izolasyon olsaydı patlamaya dayanıklı kontrol odasından sistem güvenle
     durdurulabilir, salım miktarı azaltılabilir ve can kaybı önlenebilirdi

4. YETERSİZ TEHLİKE DEĞERLENDİRMESİ (PHA/HAZOP):
   - 2014 PHA: Sıvı genleşmesiyle oluşabilecek basınç risklerine kısmen değindi; Y-filtre
     veya izolasyon vanaları çizimlerde gösterilmedi
   - 2015 PHA: Değerlendirme kapsamı sınırlıydı; 2015'teki Y-filtre çatlağı dahil
     geçmiş olaylar göz ardı edildi
   - 2018 PHA: Geçmiş olaylar dikkate alınmadı; ROSOV ihtiyacı değerlendirilmedi;
     çizimler Y-filtreyi paslanmaz çelik olarak gösterdiğinden yanlış varsayımlara yol açtı
   - OSHA denetimi (2019): "PHA analizleri Y-filtrenin risklerini içermiyordu" tespiti yapıldı
   - Ocak 2017 denetiminde 370 soruluk değerlendirmede 341 öneri sunuldu; önerilerin
     büyük çoğunluğu uygulamaya konulmamıştı

5. MOC (DEĞİŞİKLİK YÖNETİMİ) VE PSSR SÜREÇLERİNİN YETERSİZLİĞİ:
   - 2015 MOC süreci: İzobütilen tank kapasitesi artırıldı, ancak MOC dokümantasyonu
     P&ID üzerinde Y-filtrenin malzeme bilgisi veya izolasyon sistemine dair bilgi içermiyordu
   - Çek valf, izolasyon vanaları ve Y-filtre malzemesi analiz edilmeden sistem onaylandı
   - KMCO'nun kilit yönetim pozisyonlarının çoğu olay günü şirkette iki yıldan az deneyime
     sahip kişiler tarafından yürütülmekteydi; proses güvenliği sisteminin büyük bölümü
     hâlâ geliştirme aşamasındaydı

6. ACİL DURUM MÜDAHALE EKSİKLİKLERİ:
   - Tesis alarm sistemi olay sırasında DEVREYE ALINMADI; çalışanlar yalnızca telsizle
     bireysel olarak uyarıldı
   - Telsizi olmayan veya telsizli biriyle birlikte olmayan çalışanlar tehlikeden haberdar
     olamadı
   - Alarm sistemi kuralım gerektiriyordu ancak çalışanların büyük çoğunluğu alarm sistemini
     gerçek bir acil durumda nasıl kullanacağını bilmiyordu
   - Bir süpervizörün ifadesi: "Kimse alarmı nasıl çalıştıracağını bilmiyor."
   - ERP (Acil Durum Müdahale Planı) aktif olarak güncelleniyordu ancak olay günü
     geçerli ve etkili değildi
   - Vardiya süpervizörü yaklaşık iki yıldır ERT üyesi değildi; ERP süpervizörü ilk olay
     komutanı olarak görevlendiriyordu
   - Olay, planlanmış "olay komutanlığı eğitimi"nden yalnızca 3 gün önce gerçekleşti
   - OSHA tespiti: "Tahliye eğitimleri yetersizdi; acil eylem planı ve tatbikatlar
     uygulanmamıştı"

7. TUTUŞMA KAYNAĞININ KORUNMAMIŞ OLMASI:
   - R2 Binası (tutuşmanın gerçekleştiği bina), NFPA 70'e göre Class 1, Div 2 tehlikeli
     bölge olarak sınıflandırılmıştı
   - Binadaki motor çalıştırıcılar ve elektrikli bileşenler bu sınıfa UYGUN DEĞİLDİ
   - Bina pozitif basınçlı (pressurized) sistemle korunmamıştı
   - Çatlak kapılar, pencereler ve sızdırmaz olmayan duvar tipi klima ünitesi izobütilen
     buharının içeri sızmasına olanak sağladı
   - 2013'te sigorta firmaları "R2 Binası'ndaki ekipmanları ya korunaklı hale getirin ya da
     patlamaya dayanıklı odaya taşıyın" uyarısında bulunmuş; KMCO bu uyarıyı dikkate
     almamıştı

OLAY KRONOLOJİSİ:

06:25 - İzobütilen şarjı tamamlandı; saha operatörü çıkış hattındaki vanaları kapattı

10:41 - Eğitim sürecindeki Saha Operatörü 1, reaktör yakınında yüksek bir pat sesi ve
         ardından basınçlı bir boşalma sesi duydu
       - Besleme pompasının emme hattındaki 3 inçlik gri dökme demir Y-filtreden yumruk
         büyüklüğünde bir metal parça koptu
       - Yaklaşık 4.500 kg sıvı izobütilen atmosfere salınmaya başladı
       - Saha operatörü sızıntıyı teşhis edemedi (tesiste yalnızca altı aydır çalışıyordu)

10:43 - Saha Operatörü 1, Pano Operatörü 1'i yardım için çağırdı
       - İkili reaktör yolunda buluştu; Pano Operatörü 1 maddenin izobütilen olduğunu anladı

10:45 - Pano Operatörü 1 telsizle "Reaksiyon alanı tahliye edilsin" anonsu yaptı
       - Ardından kontrol odasına döndü, SCBA cihazını taktı ve tekrar sahaya çıktı

10:46 - Pano Operatörü 1 sahaya girerek manuel vanayı kapattı; izobütilen akışı durduruldu
         (ancak o zamana kadar yaklaşık 4.500 kg izobütilen serbest kalmıştı)
       - Saha Operatörü 1 yangın monitörlerini açtı, çalışanları tahliyeye yönlendirdi ve
         araç girişlerini kapattı

10:47 - Vardiya Amiri telsizden olayı öğrendi; üniteye giderek "iki ayak genişliğinde bir
         izobütilen nehri" tarif ettiği buharla karşılaştı; tüm tesisin tahliyesini emretti

10:48 - Tesis alarm sistemi DEVREYE ALINMADI; tahliye yalnızca telsizle duyuruldu
       - Telsizi olmayan çalışanlar tahliye çağrısını duymadı

10:51 - İzobütilen buhar bulutu tutuştu ve patlama gerçekleşti (tutuşma kaynağı: R2 Binası
         içindeki uygunsuz elektrikli ekipmanlar)
       - Pano Operatörü 1 buhar bulutundan geçmeye çalışırken "ateş topunun" içinde kaldı;
         ağır yanıklarla yaralandı
       - Vardiya Amiri son yangın monitörünü açtıktan hemen sonra patlamayla havaya
         savruldu; ağır yanıklarla yere düştü

11:00 (yaklaşık) - Olay mahallinin 1,6 km çevresindeki yerleşim alanları için
                    "yerinde kal" (shelter-in-place) emri verildi

11:28 - Crosby Gönüllü İtfaiyesi olay yerine ulaştı

Sonraki Analizler:
- Pano Operatörü 2'nin R2 Binası girişinde cansız bedeni bulundu; ölüm nedeni
  patlama kaynaklı kesici-delici yaralanma (brakiyal arter ve ven kesilmesi)
- Toplam 28 yaralı (5 KMCO personeli, 23 yüklenici çalışan)
- Yaklaşık 15:15'te "yerinde kal" emri kaldırıldı
- KMCO Mayıs 2020'de iflas başvurusunda bulundu; tesis Altivia tarafından satın alındı

EKİPMAN İNCELEME BULGULARI:

Y-Filtre Arızası:
- 3 inç gri dökme demir Y-filtre gövdesinden yumruk büyüklüğünde parça koptu
- Filtre batı yüzeyinde 7,5 x 14 cm boyutlarında delik oluştu
- Metalurjik testler: İç basınç nedeniyle gevrek kopma (brittle overload fracture)
- Dökme demir, kırılmadan önce herhangi bir şekil bozulması veya uyarı belirtisi VERMEZ
- 2015 yılında aynı konumda başka bir Y-filtre çatlamış; birebir değiştirilmiş,
  kök neden araştırılmamıştı (uyarı işareti görmezden gelindi)

Malzeme Uygunsuzluğu:
- NFPA 58: 1931'den beri LPG sistemlerinde dökme demir yasaktır
- CSB: Dökme demir, sıvı izobütilen gibi yanıcı maddelerin taşındığı sistemlerde
  kullanılmamalıdır
- Proses çizimlerinde Y-filtre "SS" (stainless steel) olarak gösterilmişti; gerçekte
  gri dökme demirdi; bu yanlış bilgi tüm PHA analizlerinde tehlikenin gözden kaçmasına
  yol açtı

Tutuşma Kaynağı - R2 Binası:
- R2 Binası Class 1, Div 2 tehlikeli bölge sınıflandırmasına sahipti
- İçindeki elektrikli bileşenler bu sınıfa uygun değildi
- Bina pozitif basınçlı koruma sistemine sahip değildi
- Çatlak kapı, pencere ve sızdırmaz olmayan klima üniteleri buhar girişine izin verdi

TANIK İFADELERİ:

Saha Operatörü 1:
"Y-strainer arızalandı. İzobütilen çok hızlı çıkıyordu. Yerde beyaz buharın süzüldüğünü
ve üzerinde dalgalı bir tabaka oluştuğunu gözlemledim."

Vardiya Amiri:
"İki ayak genişliğinde bir izobütilen nehri tarif ettiğim buharla karşılaştım. İçinde kendi
kendine dönen bir akışkanlık vardı."

Bir KMCO Yöneticisi:
"[Pano Operatörü 1'e] doğru bağırdım, el işaretiyle 'Hadi çıkalım, artık çıkma zamanı'
dedim. Yaklaşık 20 metre uzaktaydım. Beni duydu mu bilmiyorum."

Süpervizör (Alarm Sistemi Hakkında):
"Kimse alarmı nasıl çalıştıracağını bilmiyor."

Güvenlik Teknisyeni (Alarm Sistemi Hakkında):
"Alarm sistemimiz var. Hem de Cadillac gibi. Çok iyi bir sistem. Ama kimse onu nasıl
kullanacağını bilmiyor, çünkü eğitim verilmedi."

Bakım Süpervizörü (Y-Filtre Hakkında):
"Bu filtreye sadece sızdırdığı zaman dokunurlardı."

OSHA CEZALARI (30 Eylül 2019):
KMCO'ya 131.274 USD ceza verildi. Temel eksiklikler:
- Tahliye eğitimleri yetersizdi
- Y-filtre ve sistemdeki malzemeler belgelendirilmemişti
- Tahliye vanalarının tasarımı ve uygunluğu belgelenmemişti
- PHA analizleri Y-filtrenin risklerini içermiyordu
- Y-filtrenin testleri yapılmamıştı
- Değişiklik yönetimi (MOC) prosedürü eksikti
- Acil eylem planı ve tatbikatlar uygulanmamıştı

REGÜLASYON VE SORUŞTURMA:
- ABD Kimyasal Güvenlik Kurulu (CSB) soruşturma yürüttü
- OSHA denetimi ve yaptırım uygulandı (131.274 USD ceza)
- EPA RMP Program 3 kapsamı
- Harris County yetkilileri ve Crosby Gönüllü İtfaiyesi olaya müdahale etti
"""


def main():
    print_header("KMCO LLC - İZOBÜTİLEN PATLAMASI, YANGIN VE ÖLÜM OLAYI TEST", "=", 80)
    print(f"     Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"     Tesis: KMCO LLC, Crosby, Texas")
    print(f"     Olay: Y-filtre arızası → izobütilen buhar bulutu → patlama")
    print(f"     Sonuç: 1 ölü, 2 ağır yaralı, 28 yaralı")

    start_time = datetime.now()

    # API Key kontrolü
    print_step(1, "Ortam Kontrolü")
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        print("  ❌ OPENROUTER_API_KEY bulunamadı!")
        return
    print_success(f"API Key: {api_key[:8]}...{api_key[-4:]}")

    # Output dizini
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    print_success("Çıktı dizini hazır")

    # Test ID
    incident_id = f"kmco_patlama_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # ========================================================================
    # ADIM 2: OVERVIEW AGENT
    # ========================================================================
    print_step(2, "OverviewAgent")
    overview_agent = OverviewAgent()
    print_success("Agent başlatıldı")

    incident_dict = {"description": INCIDENT_DESCRIPTION}
    overview_result = overview_agent.process_initial_report(incident_dict)

    print_success(f"Ref No: {overview_result.get('ref_no', 'N/A')}")
    print_success(f"Olay Tipi: {overview_result.get('incident_type', 'N/A')}")

    # ========================================================================
    # ADIM 3: ASSESSMENT AGENT
    # ========================================================================
    print_step(3, "AssessmentAgent")
    assessment_agent = AssessmentAgent()
    print_success("Agent başlatıldı")

    incident_dict = {"description": INCIDENT_DESCRIPTION}
    assessment_result = assessment_agent.assess_incident(overview_result, incident_dict)

    print_success(f"Şiddet: {assessment_result.get('actual_potential_harm', 'N/A')}")
    print_success(f"RIDDOR: {assessment_result.get('riddor', {}).get('reportable', 'N/A')}")
    print_success(f"Level: {assessment_result.get('investigation', {}).get('level', 'N/A')}")

    # ========================================================================
    # ADIM 4: ROOT CAUSE AGENT V2
    # ========================================================================
    print_step(4, "RootCauseAgentV2")
    rc_agent = RootCauseAgentV2()
    print_success("Kök Neden Ajanı V2 başlatıldı (knowledge_base)")

    incident_dict = {"description": INCIDENT_DESCRIPTION}
    root_cause_result = rc_agent.analyze_root_causes(
        part1_data=overview_result,
        part2_data=assessment_result,
        investigation_data=incident_dict
    )

    branches = root_cause_result.get('branches', [])
    root_causes = root_cause_result.get('root_causes', [])

    print_success(f"Dallar: {len(branches)}")
    print_success(f"Kök nedenler: {len(root_causes)}")
    for idx, rc in enumerate(root_causes, 1):
        print(f"     [{idx}] {rc.get('hsg_code', rc.get('code', 'N/A'))} - "
              f"{rc.get('title', rc.get('standard_title_tr', rc.get('cause_tr', 'N/A')))[:60]}...")

    # JSON kaydet
    import json
    json_path = output_dir / f"{incident_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'overview': overview_result,
            'assessment': assessment_result,
            'root_cause': root_cause_result
        }, f, ensure_ascii=False, indent=2)
    print_success(f"JSON: {json_path}")

    # ========================================================================
    # ADIM 5: DOCX + HTML RAPOR
    # ========================================================================
    print_step(5, "Rapor Üretimi (DOCX + HTML)")

    docx_agent = SkillBasedDocxAgent()
    print_success("SkillBasedDocxAgent V2 hazır")

    combined_data = {
        'part1': overview_result,
        'part2': assessment_result,
        'part3_rca': root_cause_result
    }

    ref_no = overview_result.get('ref_no', 'INC-UNKNOWN')
    incident_type_raw = overview_result.get('incident_type', 'incident')
    incident_type_clean = incident_type_raw.lower().replace(' ', '_')[:30]

    output_docx = f"outputs/{ref_no}_{incident_type_clean}.docx"

    docx_path = docx_agent.generate_report(
        investigation_data=combined_data,
        output_path=output_docx
    )

    html_path = docx_path.replace('.docx', '.html')
    docx_size = os.path.getsize(docx_path) / 1024

    if os.path.exists(html_path):
        html_size = os.path.getsize(html_path) / 1024
        print_success(f"HTML: {html_size:.1f} KB - {html_path}")
    else:
        html_path = "N/A"
        print_info("HTML dosyası oluşturulmadı")

    print_success(f"DOCX: {docx_size:.1f} KB - {docx_path}")

    # ========================================================================
    # ÖZET
    # ========================================================================
    elapsed = (datetime.now() - start_time).total_seconds()

    print_header("TEST ÖZET")
    print(f"     Süre: {elapsed:.1f} saniye")
    print(f"     Sonuç: 5/5 adım başarılı")
    print_success("🎉 TÜM TESTLER BAŞARILI!")
    print()
    print("📄 Üretilen Dosyalar:")
    print(f"   • {json_path}")
    print(f"   • {docx_path}")
    print(f"   • {html_path}")


if __name__ == "__main__":
    main()
