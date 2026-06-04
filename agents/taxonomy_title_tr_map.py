"""Resmi taksonomi kodları için Türkçe kök neden başlıkları (rapor/decision tree gösterimi)."""

from __future__ import annotations

CODE_TITLE_TR: dict[str, str] = {
    "C1.1": "Duyusal Bozukluklar",
    "C1.2": "Fiziksel Kısıtlılıklar",
    "C1.3": "Tıbbi Durum veya Hastalık",
    "C1.4": "Yorgunluk (Akut veya Kronik)",
    "C1.5": "İlaç, Alkol veya İlaç Tedavisi",
    "C1.6": "Vardiya Düzeni ve Sirkadiyen Bozulma",
    "C2.1": "Bellek veya Dikkat Kısıtlılığı",
    "C2.2": "Zayıf Koordinasyon veya Tepki Süresi",
    "C2.3": "Zayıf Mekanik/Sistem Kavrayışı",
    "C2.4": "Yetersiz Yargı veya Karar Verme",
    "C2.5": "Performansı Etkileyen Duygusal Durum",
    "C2.6": "Göreve Özgü Zihinsel Model Eksikliği",
    "C3.1": "Gerekli Beceri Değerlendirmesi Yetersiz",
    "C3.2": "Yetersiz Beceri Pratiği",
    "C3.3": "Beceri Koçluğu Yapılmadı",
    "C3.4": "Beceri Nadiren Uygulandı veya Zayıfladı",
    "C3.5": "Yanlış Davranış Ödüllendirildi",
    "C3.6": "Doğru Davranış Ödüllendirilmedi",
    "C3.7": "Görev Değişikliği Yetkinlik Açığı",
    "D1.1": "Zayıf Liderlik Taahhüdü",
    "D1.2": "Yetersiz Gözetim",
    "D1.3": "Hesap Verebilirlik Eksikliği",
    "D1.4": "Üretim Baskısı",
    "D1.5": "Sapma Normalleşmesi",
    "D1.6": "Etkisiz Durdurma Yetkisi",
    "D1.7": "Zayıf Bildirim/Öğrenme Kültürü",
    "D1.8": "Yetersiz Görünür Liderlik",
    "D1.9": "Yönetimin Bilinen Sapmaları Tolere Etmesi",
    "D1.10": "Liderlerin Davranışları Pekiştirmemesi",
    "D1.11": "Psikolojik Güvenlik Eksikliği",
    "D2.1": "Yatay İletişim Yetersiz",
    "D2.2": "Dikey İletişim Yetersiz",
    "D2.3": "Kurumlar Arası İletişim",
    "D2.4": "Vardiya Devir Teslimi Yetersiz",
    "D2.5": "İletişim Uygulanmadı",
    "D2.6": "Yanlış/Eksik Bilgi",
    "D2.7": "Bilginin Yanlış Anlaşılması",
    "D2.8": "Teknik Dokümantasyon Güncelliği",
    "D3.1": "Eğitim Sağlanmadı",
    "D3.2": "Eğitim Tasarımı Etkisiz",
    "D3.3": "Eğitim Bilgi Aktarımı Etkisiz",
    "D3.4": "Bilginin Unutulması",
    "D3.5": "Kritik Yetkinlik Açıkları",
    "D4.1": "Risk Değerlendirmesi Yetersiz",
    "D4.2": "Risk Kontrolleri Uygulanmadı",
    "D4.3": "Değişim Yönetimi (MoC) Etkisiz",
    "D4.4": "İş İzni Sistemi (PTW) Başarısızlığı",
    "D4.5": "Enerji İzolasyonu (LOTO) Etkisiz",
    "D4.6": "Geçici Risk Kontrollerinin Kalıcı Sayılması",
    "D4.7": "İş Kapsamı Değişikliği",
    "D4.8": "Çalışma Alanı Güvenli Bırakılmadı",
    "D4.9": "Eş Zamanlı Operasyonlar (SIMOPS)",
    "D4.10": "Bariyer Yönetimi Yetersizliği",
    "D5.1": "Teknik Tasarım Hataları",
    "D5.2": "Tasarım Girdileri Hatalı",
    "D5.3": "Ergonomik Tasarım Hataları",
    "D5.4": "Kurulum Gözetimi Yetersiz",
    "D5.5": "Operasyonel Hazırlık (PSSR) Açıkları",
    "D5.6": "Erken Dönem İzleme Yetersiz",
    "D5.7": "Teknik Risk Analizleri (HAZOP/LOPA) Eksik",
    "D5.8": "Doğası Gereği Daha Güvenli Tasarım (ISD) Göz Ardı Edildi",
    "D6.1": "Bakım Stratejisi Yetersiz",
    "D6.2": "Bakım Uygulaması Yetersiz",
    "D6.3": "Muayene/Kalibrasyon Yetersiz",
    "D6.4": "Dokümantasyon Yetersiz",
    "D6.5": "Tekrarlayan Arızalar (KNA Açığı)",
    "D6.6": "Ertelenmiş Bakımın Normalleşmesi",
    "D6.7": "Yanlış Strateji",
    "D6.8": "KSE Tanımlanmadı",
    "D7.1": "Yüklenici Ön Yeterliliği Yok",
    "D7.2": "Ön Yeterlilik Etkisiz",
    "D7.3": "Onaysız Yüklenici Kullanımı",
    "D7.4": "Seçim Süreci Etkisiz",
    "D7.5": "İş Gözetimi Etkisiz",
    "D7.6": "Zayıf Kültür Entegrasyonu",
    "D8.1": "Yanlış Ürün Siparişi",
    "D8.2": "Yanlış Ürün Teslimi",
    "D8.3": "Taşıma Hasarı",
    "D8.4": "Depolama Yetersizliği",
    "D8.5": "Etiketleme Yetersizliği",
    "D8.6": "Sahte/Şüpheli Malzeme",
    "D9.1": "Görev İçin SPP Yok",
    "D9.2": "SPP Geliştirme Etkisiz",
    "D9.3": "İletişim/Erişim Etkisiz",
    "D9.4": "Uygulanabilirlik Zayıf",
    "D9.5": "İzleme ve Denetim Yetersiz",
    "D10.1": "Planlar/Tatbikatlar Yetersiz",
    "D10.2": "Ekipman Etkisiz",
    "D10.3": "Koordinasyon Açıkları",
    "D10.4": "Dış Olaylar",
    "D10.5": "Roller Belirsiz",
    "D10.6": "MAH Müdahale Planlaması Yok",
}


def title_tr_for_code(code: str, fallback_en: str = "") -> str:
    """
    Resmi Türkçe yaprak başlık.
    Öncelik: BARSEL taksonomi JSON → CODE_TITLE_TR (legacy) → fallback_en.
    """
    key = (code or "").strip().upper()
    if not key:
        return (fallback_en or "").strip()
    try:
        from agents.barsel_taxonomy import barsel_taxonomy_enabled, official_title_tr_for_code
    except ImportError:
        from .barsel_taxonomy import barsel_taxonomy_enabled, official_title_tr_for_code

    if barsel_taxonomy_enabled():
        official = official_title_tr_for_code(key)
        if official:
            return official
    if key in CODE_TITLE_TR:
        return CODE_TITLE_TR[key]
    return (fallback_en or "").strip()
