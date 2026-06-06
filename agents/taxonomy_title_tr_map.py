"""Resmi taksonomi kodları için Türkçe başlıklar (rapor / decision tree).

- GROUP_TITLE_TR: C1, D4 … ana grup → Kritik Faktör başlığı (kodsuz)
- CODE_TITLE_TR: C1.1, D4.3 … yaprak → Kök neden başlığı (kodsuz)

Kaynak: BARSEL C/D tablosu (barsel_taxonomy_multilingual.json ile hizalı).
"""

from __future__ import annotations

import re

# Ana grup — Kritik Faktör (KRİTİK FAKTÖR N - …)
GROUP_TITLE_TR: dict[str, str] = {
    "C1": "Fiziksel Kapasite ve Sağlık",
    "C2": "Bilişsel ve Zihinsel Yeterlilik / Yetenek",
    "C3": "BECERİ DÜZEYİ, YETKİNLİK, YETERLİLİK VE DAVRANIŞSAL ŞARTLANMA",
    "D1": "Liderlik, gözetim ve güvenlik kültürü",
    "D2": "İletişim ve Bilgi Yönetimi",
    "D3": "Eğitim, yetkinlik ve işgücü yönetimi",
    "D4": "RİSK VE İŞ KONTROL SİSTEMLERİ",
    "D5": "Mühendislik / Tasarım ve Teknik Sistemler",
    "D6": "Bakım, varlık bütünlüğü ve güvenilirlik",
    "D7": "Yüklenici ve Tedarik Zinciri Yönetimi",
    "D8": "SATIN ALMA, MALZEME TAŞIMA VE MALZEME KONTROLÜ",
    "D9": "Standartlar / Pratikler / Prosedürler (SPP)",
    "D10": "Acil durum hazırlığı",
}

# Yaprak kod — Kök neden kutusu
CODE_TITLE_TR: dict[str, str] = {
    # C — Kişisel faktörler
    "C1.1": "Duyusal Bozukluklar (Görme, İşitme, Diğer Duyular)",
    "C1.2": "Fiziksel Kısıtlamalar (Boy, Güç, Hareket Kabiliyeti vb.)",
    "C1.3": "Tıbbi Durumlar veya Hastalık",
    "C1.4": "Yorgunluk (Akut veya Kronik)",
    "C1.5": "Uyuşturucu, Alkol veya İlaç Etkisi – Madde Hassasiyeti ve Alerjiler",
    "C1.6": "Vardiya Düzeninin Yarattığı Sirkadiyen Bozukluk",
    "C2.1": "Hafıza veya Dikkat Kısıtlamaları",
    "C2.2": "Zayıf Koordinasyon veya Tepki (Reaksiyon) Süresi",
    "C2.3": "Zayıf Mekanik Anlama Yeteneği veya Sistem Kavrayışı",
    "C2.4": "Yetersiz Muhakeme veya Karar Verme Yeteneği",
    "C2.5": "Performansı Etkileyen Duygusal Durum",
    "C2.6": "Göreve Özgü Zihinsel Modellerin Eksikliği – Düşük Öğrenme Yeteneği",
    "C3.1": "GEREKLİ BECERİ VEYA YETERLİLİĞİN DEĞERLENDİRİLMESİ YETERSİZ",
    "C3.2": "YETERSİZ BECERİ UYGULAMASI",
    "C3.3": "BECERİ KOÇLUĞU YAPILMAMIŞ VEYA GERİ BİLDİRİM EKSİKLİĞİ",
    "C3.4": "BECERİNİN NADİREN UYGULANMASI VEYA KÖRELMESİ",
    "C3.5": "HATALI DAVRANIŞIN ÖDÜLLENDİRİLMESİ VEYA DÜZELTİLMEMESİ",
    "C3.6": "DOĞRU DAVRANIŞIN ÖDÜLLENDİRİLMEMESİ",
    "C3.7": "GÖREV DEĞİŞİKLİĞİ VEYA ROTASYONA BAĞLI YETKİNLİK KAYBI",
    # D — Organizasyonel faktörler
    "D1.1": "Güvenliğe yönelik zayıf liderlik taahhüdü",
    "D1.2": "Yetersiz gözetim veya denetim",
    "D1.3": "Hesap verebilirlik (accountability) eksikliği",
    "D1.4": "Üretim baskısının güvenliğin önüne geçmesi",
    "D1.5": "Sapmaların normalleşmesi (kanıksama)",
    "D1.6": "Etkisiz iş durdurma yetkisi (stop-work authority)",
    "D1.7": "Zayıf raporlama ve öğrenme kültürü",
    "D1.8": "Yetersiz görünür saha liderliği",
    "D1.9": "Yönetimin bilinen sapmalara tolerans göstermesi",
    "D1.10": "Liderlerin güvenlik davranışlarını pekiştirmemesi",
    "D1.11": "Psikolojik güvenlik ortamının yokluğu",
    "D2.1": "Yatay İletişim Yetersizliği (Aynı Seviyedeki Çalışanlar Arası)",
    "D2.2": "Dikey İletişim Yetersizliği (Yönetici–Çalışan Arası)",
    "D2.3": "Organizasyonlar / Birimler Arası İletişim Yetersizliği",
    "D2.4": "Vardiyalar Arası İletişim (Handover) Yetersizliği",
    "D2.5": "İletişim Gerçekleşmedi veya Hedefe Ulaşmadı",
    "D2.6": "Yanlış veya Eksik Bilgi İletilmesi",
    "D2.7": "Bilginin Alıcı Tarafından Yanlış Anlaşılması",
    "D2.8": "Teknik Dokümantasyon Güncelliğinin Yönetilmemesi",
    "D3.1": "Eğitimin sağlanmaması / verilmemesi",
    "D3.2": "Eğitim tasarımının ve içeriğinin etkisiz olması",
    "D3.3": "Eğitimde bilgi aktarımının etkisiz olması",
    "D3.4": "Bilginin iş başında pekişmemesi ve unutulması",
    "D3.5": "Kritik yetkinliklerin işgücü planlamasına entegre edilmemesi",
    "D4.1": "İş Planlaması veya Risk Değerlendirmesinin Yapılmaması ya da Yetersiz Olması",
    "D4.2": "Risk Kontrollerinin Uygulanmaması veya Sahaya Yansımaması",
    "D4.3": "Değişim Yönetiminin Etkisiz Olması veya Atlanması",
    "D4.4": "İş İzin Sisteminin Olmaması, Gerekli İznin Alınmaması veya Etkisiz Olması",
    "D4.5": "Enerji İzolasyonunun (EKED) Etkisiz Olması",
    "D4.6": "Geçici Risk Kontrollerinin Kalıcı Muamele Görmesi",
    "D4.7": "Kapsam Değişikliği ve İzin Güncellemesinin Yapılmaması",
    "D4.8": "İş Yerinin Emniyetli Bırakılmaması",
    "D4.9": "Bariyer Yönetiminin Yetersizliği",
    "D4.10": "Eş Zamanlı Operasyonların (SIMOPS) Yönetiminin Yetersizliği",
    "D5.1": "Teknik tasarım hataları veya uygunsuzluklar",
    "D5.2": "Tasarım girdileri, standartlar veya teknik şartnamelerin hatalı olması",
    "D5.3": "Ergonomik / insan faktör tasarım hataları",
    "D5.4": "İnşaat / montaj denetiminin etkisiz olması",
    "D5.5": "Operasyonel hazır olma (PSSR) eksiklikleri",
    "D5.6": "İlk işletme döneminde operasyon izlemesinin yetersizliği",
    "D5.7": "Risk için teknik analizlerin (PHA/HAZOP/LOPA vb.) eksik veya etkisiz olması",
    "D5.8": "Doğasında Daha Güvenli Tasarım prensiplerinin göz ardı edilmesi",
    "D6.1": "Bakım stratejisi veya planlamasının olmaması / yetersiz olması",
    "D6.2": "Bakım uygulamasının veya işçiliğin yetersiz olması",
    "D6.3": "Muayene, test veya kalibrasyonun yetersiz olması",
    "D6.4": "Bakım dokümantasyonu ve kayıtlarının yetersizliği",
    "D6.5": "Tekrarlayan arızalardan ders alınmaması (KNA / DÖF eksikliği)",
    "D6.6": "Bakım faaliyetlerinin sistematik olarak ertelenmesi",
    "D6.7": "Yanlış bakım tipi / stratejisi seçilmesi",
    "D6.8": "Güvenlik Kritik Ekipmanların (GKE) tanımlanmaması veya ayrı yönetilmemesi",
    "D7.1": "Yüklenici ön yeterlilik süreci yok",
    "D7.2": "Yüklenici ön yeterlilik süreci etkisiz",
    "D7.3": "Onaylanmamış yüklenici kullanımı",
    "D7.4": "Yüklenici seçimi etkisiz (güvenliğin yetersiz ağırlıklandırılması)",
    "D7.5": "Yüklenici süreçleri denetimi yok veya etkisiz",
    "D7.6": "Zayıf yüklenici güvenlik kültürü entegrasyonu",
    "D8.1": "Yanlış ürünün sipariş edilmesi",
    "D8.2": "Yanlış ürünün teslim alınması (kabul kontrolünün yetersizliği)",
    "D8.3": "Taşıma veya sevkiyat sırasında malzeme hasarı",
    "D8.4": "Malzeme depolama yetersizliği",
    "D8.5": "Malzeme etiketleme ve işaretlemesinin yetersizliği",
    "D8.6": "Sahte veya şüpheli malzeme / onaysız parça kullanımı",
    "D9.1": "Görev için SPP’nin olmaması",
    "D9.2": "SPP geliştirilmesinin etkisiz olması",
    "D9.3": "SPP iletişim ve erişiminin etkisiz olması",
    "D9.4": "SPP’nin saha koşullarında uygulanabilir olmaması",
    "D9.5": "SPP’nin uygulanmasının izlenmemesi ve denetlenmemesi",
    "D10.1": "Acil durum planları veya tatbikatlarının yetersizliği",
    "D10.2": "Acil durum ekipmanının mevcut olmaması veya etkisizliği",
    "D10.3": "Dış kurumlarla zayıf koordinasyon",
    "D10.4": "Acil durum müdahale rol ve sorumluluklarının belirsizliği",
    "D10.5": "Büyük kaza tehlikelerine (BKT) özel acil durum planlamasının yokluğu",
    "D10.6": "Organizasyonel kontrol dışındaki dış olaylara hazırlıksızlık",
}


def _group_id_from_code(code: str) -> str:
    """D4.3 → D4, D10.2 → D10, D4 → D4."""
    key = (code or "").strip().upper()
    if not key:
        return ""
    if re.match(r"^[CD]\d+$", key):
        return key
    m = re.match(r"^([CD]\d+)\.", key)
    return m.group(1) if m else ""


def group_title_tr_for_code(code: str) -> str:
    """
    Ana grup başlığı (Kritik Faktör): C1, D4, D8 …
    Yaprak kod (D4.3) veya grup kodu (D4) kabul eder.
    """
    gid = _group_id_from_code(code)
    return GROUP_TITLE_TR.get(gid, "")


def title_tr_for_code(code: str, fallback_en: str = "") -> str:
    """
    Yaprak kök neden başlığı (C1.1, D4.3 …).
    Öncelik: CODE_TITLE_TR (resmi tablo) → BARSEL JSON → fallback_en.
    """
    key = (code or "").strip().upper()
    if not key:
        return (fallback_en or "").strip()
    if key in CODE_TITLE_TR:
        return CODE_TITLE_TR[key]
    try:
        from agents.barsel_taxonomy import barsel_taxonomy_enabled, official_title_tr_for_code
    except ImportError:
        from .barsel_taxonomy import barsel_taxonomy_enabled, official_title_tr_for_code

    if barsel_taxonomy_enabled():
        official = official_title_tr_for_code(key)
        if official:
            return official
    return (fallback_en or "").strip()
