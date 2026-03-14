"""
Hybrid Input Processor - Girdi Seviyesi Tespit Modülü
Test versiyonu - Ana sistemi değiştirmez
"""

from typing import Dict, List, Tuple
import re


class HybridInputProcessor:
    """
    Kullanıcı girdisini analiz eder ve eksiklikleri tespit eder.
    
    Seviyeler:
    - Level 1 (8+ puan): Detaylı rapor (test formatı gibi)
    - Level 2 (4-7 puan): Orta detay (form girişi gibi)
    - Level 3 (0-3 puan): Minimal (serbest metin)
    """
    
    # Anahtar kelime setleri
    KEYWORDS = {
        "kronoloji": ["kronoloji", "timeline", "saat:", "tarih:", "zaman:"],
        "prosedür": ["prosedür", "procedure", "LOTO", "iş izni", "permit", "yönerge"],
        "tanık": ["tanık", "witness", "beyan", "statement", "ifade"],
        "yönetim": ["yönetim", "management", "baskı", "pressure", "kültür", "amir", "şef"],
        "ekipman": ["ekipman", "equipment", "arıza", "failure", "bakım", "maintenance"],
        "eğitim": ["eğitim", "training", "sertifika", "certificate", "kurs"],
        "ppe": ["KKD", "PPE", "eldiven", "glove", "baret", "helmet", "koruyucu"],
    }
    
    def __init__(self):
        pass
    
    def detect_input_level(self, incident_text: str) -> Tuple[int, Dict]:
        """
        Girdi seviyesini tespit eder.
        
        Returns:
            (level, details)
        """
        text_lower = incident_text.lower()
        
        # Anahtar kelime taraması
        keywords_found = {}
        for category, keywords in self.KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            keywords_found[category] = count > 0
        
        # Detay göstergeleri
        indicators = {
            "has_timeline": any(k in text_lower for k in ["kronoloji", "timeline", "saat:"]),
            "has_witness": any(k in text_lower for k in ["tanık", "witness", "beyan"]),
            "has_procedure": any(k in text_lower for k in ["prosedür", "loto", "iş izni"]),
            "has_root_cause": any(k in text_lower for k in ["kök neden", "root cause", "neden:"]),
            "has_management": any(k in text_lower for k in ["yönetim", "management", "baskı"]),
            "word_count": len(incident_text.split()),
        }
        
        # Seviye belirleme (puanlama sistemi)
        detail_score = sum([
            indicators["has_timeline"] * 2,
            indicators["has_witness"] * 2,
            indicators["has_procedure"] * 2,
            indicators["has_root_cause"] * 3,
            indicators["has_management"] * 2,
            (indicators["word_count"] > 500) * 2,
        ])
        
        if detail_score >= 8:
            level = 1  # Detaylı
        elif detail_score >= 4:
            level = 2  # Orta
        else:
            level = 3  # Minimal
        
        # Mevcut ve eksik bilgileri listele
        present = [k for k, v in keywords_found.items() if v]
        missing = [k for k, v in keywords_found.items() if not v]
        
        return level, {
            "present": present,
            "missing": missing,
            "keywords_found": keywords_found,
            "indicators": indicators,
            "detail_score": detail_score,
        }
    
    def generate_missing_questions(self, missing_categories: List[str], 
                                   incident_type: str = "generic") -> List[Dict]:
        """
        Eksik kategoriler için sorular üretir.
        """
        questions = []
        
        # Olay tipine göre özelleştirilmiş sorular
        question_templates = {
            "elektrik": {
                "prosedür": "LOTO (Lockout/Tagout) prosedürü uygulandı mı?",
                "ppe": "Elektrikçi eldiveni ve yalıtımlı ayakkabı kullanıldı mı?",
                "ekipman": "Elektrik paneli son bakımı ne zaman yapıldı?",
            },
            "düşme": {
                "prosedür": "Yüksekte çalışma izni alındı mı?",
                "ppe": "Emniyet kemeri takılı mıydı?",
                "ekipman": "Korkuluk/güvenlik ağı var mıydı?",
            },
            "forklift": {
                "prosedür": "Forklift kullanım izni var mıydı?",
                "ppe": "Sürücü emniyet kemeri takıyor muydu?",
                "ekipman": "Forklift ikaz sistemi çalışıyor muydu?",
            },
            "generic": {
                "prosedür": "İş için özel bir prosedür var mıydı?",
                "ppe": "Gerekli koruyucu ekipman kullanıldı mı?",
                "ekipman": "Ekipman düzenli bakıma tabi miydi?",
                "eğitim": "Personel bu iş için eğitim almış mıydı?",
                "yönetim": "Yönetim denetim yaptı mı?",
            }
        }
        
        templates = question_templates.get(incident_type, question_templates["generic"])
        
        for category in missing_categories:
            if category in templates:
                questions.append({
                    "category": category,
                    "question": templates[category],
                    "options": self._get_default_options(category),
                })
        
        return questions
    
    def _get_default_options(self, category: str) -> List[Dict]:
        """Kategoriye göre varsayılan cevap seçenekleri"""
        
        if category == "prosedür":
            return [
                {"label": "Hayır, prosedür hiç yoktu", "code": "D4.1"},
                {"label": "Evet, prosedür vardı ama uygulanmıyordu", "code": "D4.2"},
                {"label": "Prosedür genelde uygulanır, bu sefer atlandı", "code": "A1.1"}
            ]
        
        elif category == "eğitim":
            return [
                {"label": "Hayır, eğitim verilmemişti", "code": "D3.1"},
                {"label": "Eğitim verilmişti ama yeterli değildi", "code": "D3.1"},
                {"label": "Eğitim verilmişti ve yeterliydi", "code": None}
            ]
        
        elif category == "yönetim":
            return [
                {"label": "Yönetim sapmaları biliyordu ama tolerans gösterdi", "code": "D1.9"},
                {"label": "Üretim baskısı güvenliği bastırdı", "code": "D1.4"},
                {"label": "Denetim/gözetim yetersizdi", "code": "D1.2"}
            ]
        
        else:
            return [
                {"label": "Evet", "code": None},
                {"label": "Hayır", "code": None},
                {"label": "Kısmen", "code": None},
            ]


if __name__ == "__main__":
    # Test
    processor = HybridInputProcessor()
    
    # Test 1: Minimal giriş
    text1 = "Forklift geri giderken çalışana çarptı."
    level1, details1 = processor.detect_input_level(text1)
    print(f"Test 1 - Minimal: Level {level1}, Eksik: {details1['missing']}")
    
    # Test 2: Detaylı giriş
    text2 = """
    OLAY RAPORU - ELEKTRİK ÇARPMASI
    Tarih: 20 Şubat 2026, Saat: 15:20
    
    OLAY KRONOLOJİSİ:
    - 14:30 - Arıza bildirildi
    - 15:20 - Elektrik çarptı
    
    LOTO PROSEDÜRÜ: Uygulanmadı
    
    TANIK BEYANI: "Kemal acele ediyordu"
    
    YÖNETİM FAKTÖRÜ: Üretim baskısı
    """
    level2, details2 = processor.detect_input_level(text2)
    print(f"Test 2 - Detaylı: Level {level2}, Mevcut: {details2['present']}")
