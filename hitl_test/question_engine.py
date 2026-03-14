"""
Question Engine - HSG245 Knowledge Base ile Entegre Soru Üretimi
Knowledge base'deki taxonomy'ye göre kontekstüel sorular üretir.

AMAÇ:
- Olay girişi sonrası eksik bilgileri tespit et
- HSG245 kodlarına göre hedeflenmiş sorular sor
- Root cause analizi için gerekli detayları topla
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.knowledge_base import HSG245_TAXONOMY


class QuestionEngine:
    """HSG245 taxonomy'ye dayalı soru üretim motoru"""
    
    def __init__(self):
        self.taxonomy = HSG245_TAXONOMY
        
        # Kategori bazlı soru şablonları (HSG245 kodlarıyla bağlantılı)
        self.question_templates = {
            "kronoloji": {
                "description": "Olayın zamansal akışı",
                "hsg245_codes": ["A1.1", "A1.2", "A4.1", "A4.2", "A4.3"],
                "questions": [
                    {
                        "question": "Olay hangi tarih ve saatte meydana geldi?",
                        "hsg245_link": "Zaman faktörü birçok davranış kodunu etkiler",
                        "required": True
                    },
                    {
                        "question": "Olay öncesi son 2 saat içinde ne tür aktiviteler yapılıyordu?",
                        "hsg245_link": "A4.1 (Yorgunluk), A4.2 (Dikkat dağınıklığı)",
                        "required": False
                    },
                    {
                        "question": "Olayın başlangıcından sonuçlanmasına kadar geçen süre ne kadardı?",
                        "hsg245_link": "A4.3 (Hızlı hareket), A5.3 (Acele etme)",
                        "required": False
                    }
                ]
            },
            
            "prosedür": {
                "description": "İş talimatları ve prosedürler",
                "hsg245_codes": ["A1.1", "A1.5", "A1.6", "A1.7", "A1.8", "D4.1"],
                "questions": [
                    {
                        "question": "Bu iş için yazılı bir prosedür/iş talimatı var mıydı?",
                        "hsg245_link": "D4.1 (Prosedür yokluğu) vs A1.1 (Prosedür ihlali)",
                        "required": True
                    },
                    {
                        "question": "Prosedür sahada uygulanabilir miydi, yoksa kağıt üzerinde mi kaldı?",
                        "hsg245_link": "A1.6 (Uygulanamaz prosedür) vs A1.8 (Gerçekçi olmayan varsayımlar)",
                        "required": True
                    },
                    {
                        "question": "Prosedürün son güncellenme tarihi nedir?",
                        "hsg245_link": "A1.5 (Güncel olmayan prosedür)",
                        "required": False
                    },
                    {
                        "question": "Çalışan bu prosedürü biliyor muydu ve eğitim almış mıydı?",
                        "hsg245_link": "D3.1 (Yetersiz eğitim) vs A1.1 (Bilinçli ihlal)",
                        "required": True
                    }
                ]
            },
            
            "tanık": {
                "description": "Görgü tanıkları ve gözlemler",
                "hsg245_codes": ["A1.2", "A1.3", "D1.9", "D2.1"],
                "questions": [
                    {
                        "question": "Olay sırasında başka kimler alanda bulunuyordu?",
                        "hsg245_link": "A1.2 (Grup ihlali), D2.1 (Yetersiz iletişim)",
                        "required": True
                    },
                    {
                        "question": "Gözetmen/formen olay sırasında oradaydı mı? Ne gördü?",
                        "hsg245_link": "A1.3 (Yönetim ihlali), D1.9 (Göz yumma)",
                        "required": True
                    },
                    {
                        "question": "Tanıklar olaydan önce bir anormallik fark etti mi?",
                        "hsg245_link": "B2.7 (Fark edilmeyen arıza), D2.3 (Raporlama eksikliği)",
                        "required": False
                    }
                ]
            },
            
            "yönetim": {
                "description": "Yönetim kontrolü ve gözetim",
                "hsg245_codes": ["D1.1", "D1.4", "D1.5", "D1.9", "D7.1", "D7.2"],
                "questions": [
                    {
                        "question": "Bu iş için gözetim/denetim planlandı mı? Kim sorumlu?",
                        "hsg245_link": "D1.1 (Yetersiz liderlik), D7.1 (Organizasyon eksikliği)",
                        "required": True
                    },
                    {
                        "question": "Yönetim daha önce benzer bir sapma/riski biliyor muydu?",
                        "hsg245_link": "D1.9 (Göz yumma), D1.4 (Yanlış önceliklendirme)",
                        "required": True
                    },
                    {
                        "question": "Risk değerlendirmesi yapılmış mıydı? Ne zaman?",
                        "hsg245_link": "D5.3 (Risk değerlendirme eksikliği)",
                        "required": True
                    },
                    {
                        "question": "Güvenlik toplantıları/toolbox talks düzenli yapılıyor mu?",
                        "hsg245_link": "D1.5 (Güvenlik önceliği eksikliği)",
                        "required": False
                    }
                ]
            },
            
            "ekipman": {
                "description": "Kullanılan ekipman ve aletler",
                "hsg245_codes": ["A2.1", "A2.2", "A2.3", "B2.1", "B2.3", "D5.1", "D6.1"],
                "questions": [
                    {
                        "question": "Hangi ekipman/alet kullanıldı? Amacına uygun muydu?",
                        "hsg245_link": "A2.1 (Uygunsuz kullanım), D5.1 (Yanlış ekipman seçimi)",
                        "required": True
                    },
                    {
                        "question": "Ekipman/aletin son bakım/muayene tarihi neydi?",
                        "hsg245_link": "D6.1 (Bakım eksikliği), B2.1 (Bakım arızası)",
                        "required": True
                    },
                    {
                        "question": "Ekipmanda bilinen bir arıza veya sorun var mıydı?",
                        "hsg245_link": "A2.3 (Arızası bilinen ekipman kullanımı)",
                        "required": True
                    },
                    {
                        "question": "Ekipman tasarım limitleri içinde mi kullanıldı?",
                        "hsg245_link": "A2.6 (Limit aşımı), D5.1 (Tasarım hatası)",
                        "required": False
                    }
                ]
            },
            
            "eğitim": {
                "description": "Eğitim ve yeterlilik",
                "hsg245_codes": ["D3.1", "D3.2", "D3.3", "C1.1", "C1.2"],
                "questions": [
                    {
                        "question": "Çalışan bu işi yapmak için eğitim almış mıydı? Ne zaman?",
                        "hsg245_link": "D3.1 (Yetersiz eğitim)",
                        "required": True
                    },
                    {
                        "question": "Çalışanın bu işte kaç yıllık deneyimi var?",
                        "hsg245_link": "C1.1 (Deneyimsizlik), C1.2 (Yetersiz yeterlilik)",
                        "required": True
                    },
                    {
                        "question": "Eğitim teorik miydi, pratik miydi, yoksa her ikisi de mi?",
                        "hsg245_link": "D3.2 (Yetersiz eğitim içeriği)",
                        "required": False
                    },
                    {
                        "question": "Periyodik tazeleme eğitimleri yapılıyor mu?",
                        "hsg245_link": "D3.3 (Eğitim takibi eksikliği)",
                        "required": False
                    }
                ]
            },
            
            "ppe": {
                "description": "Kişisel Koruyucu Donanım",
                "hsg245_codes": ["A3.1", "A3.2", "A3.3", "A3.4", "A3.6", "D3.1"],
                "questions": [
                    {
                        "question": "Bu iş için hangi KKD'ler gerekliydi?",
                        "hsg245_link": "A3.1 (İhtiyaç farkındalığı)",
                        "required": True
                    },
                    {
                        "question": "Çalışan gerekli tüm KKD'leri kullanıyor muydu?",
                        "hsg245_link": "A3.2 (KKD kullanmama) vs A3.3 (Yanlış kullanım)",
                        "required": True
                    },
                    {
                        "question": "KKD'ler sahada hazır ve erişilebilir miydi?",
                        "hsg245_link": "A3.4 (KKD yokluğu)",
                        "required": True
                    },
                    {
                        "question": "KKD'ler rahatsızlık veriyor muydu veya iş performansını etkiliyordu mu?",
                        "hsg245_link": "A3.6 (Rahatsız edici KKD)",
                        "required": False
                    }
                ]
            },
            
            "çevre": {
                "description": "Çevresel koşullar",
                "hsg245_codes": ["B1.1", "B1.4", "B3.1", "B3.2", "B4.1"],
                "questions": [
                    {
                        "question": "Olay sırasında hava koşulları nasıldı? (yağmur, rüzgar, sıcaklık)",
                        "hsg245_link": "B3.1 (Zayıf hava koşulları)",
                        "required": False
                    },
                    {
                        "question": "Çalışma alanının aydınlatması yeterli miydi?",
                        "hsg245_link": "B1.4 (Yetersiz aydınlatma)",
                        "required": True
                    },
                    {
                        "question": "Gürültü, titreşim veya diğer çevresel faktörler var mıydı?",
                        "hsg245_link": "B1.1 (Gürültü/titreşim)",
                        "required": False
                    },
                    {
                        "question": "Çalışma alanı düzenli ve tertipli miydi?",
                        "hsg245_link": "B4.1 (Kötü housekeeping), B3.2 (Yetersiz çalışma alanı)",
                        "required": True
                    }
                ]
            }
        }
    
    def generate_questions_for_missing_categories(self, missing_categories: list, incident_type: str = None) -> list:
        """
        Eksik kategoriler için HSG245'e bağlı sorular üret
        
        Args:
            missing_categories: Eksik kategori listesi (örn: ['kronoloji', 'prosedür'])
            incident_type: Olay türü (opsiyonel, gelecekte özelleştirme için)
            
        Returns:
            Soru listesi [{"category": "...", "question": "...", "hsg245_link": "...", "required": bool}]
        """
        questions = []
        
        for category in missing_categories:
            if category in self.question_templates:
                template = self.question_templates[category]
                
                # Her kategoriden sorular ekle
                for q in template["questions"]:
                    questions.append({
                        "category": category,
                        "category_description": template["description"],
                        "hsg245_codes": ", ".join(template["hsg245_codes"]),
                        "question": q["question"],
                        "hsg245_link": q["hsg245_link"],
                        "required": q["required"]
                    })
        
        return questions
    
    def get_code_specific_questions(self, suspected_codes: list) -> list:
        """
        Şüphelenilen HSG245 kodlarına göre özelleştirilmiş sorular
        
        Args:
            suspected_codes: Olası HSG245 kodları (örn: ['A1.1', 'D3.1'])
            
        Returns:
            Kod-spesifik soru listesi
        """
        code_questions = {
            # A - DAVRANIŞLAR
            "A1.1": [
                "Çalışan kuralı/prosedürü biliyor muydu?",
                "İhlal daha önce de yapılmış mıydı?",
                "İhlal sonrası bir yaptırım uygulandı mı?"
            ],
            "A1.2": [
                "Tüm ekip aynı şekilde mi çalışıyordu?",
                "Bu sapma ekipte 'norm' haline gelmiş miydi?",
                "Ekip lideri bu durumdan haberdar mıydı?"
            ],
            "A1.5": [
                "Prosedürün son güncelleme tarihi nedir?",
                "Prosedür gerçek saha koşullarını yansıtıyor mu?",
                "Prosedür gözden geçirme süreci var mı?"
            ],
            "A2.3": [
                "Arızanın ne zaman başladığı biliniyordu mu?",
                "Arıza neden rapor edilmemişti?",
                "Arızanın etiketi/bildirimi var mıydı?"
            ],
            "A3.2": [
                "Çalışan KKD kullanmama nedenini açıkladı mı?",
                "KKD rahatsızlık veriyor muydu?",
                "Başka çalışanlar KKD kullanıyor muydu?"
            ],
            
            # B - KOŞULLAR
            "B2.1": [
                "Ekipmanın bakım planı var mıydı?",
                "Son bakım ne zaman yapılmıştı?",
                "Bakım kayıtları tutuldu mu?"
            ],
            "B1.4": [
                "Aydınlatma ölçümü yapılmış mıydı?",
                "Çalışanlar daha önce aydınlatmadan şikayet etti mi?",
                "Aydınlatma standarda uygun muydu?"
            ],
            
            # C - KİŞİSEL FAKTÖRLER
            "C1.1": [
                "Çalışanın bu işte kaç günlük deneyimi var?",
                "Oryantasyon/işbaşı eğitimi verildi mi?",
                "Deneyimli birisi gözetim yapıyor muydu?"
            ],
            "C2.1": [
                "Çalışan son 24 saatte kaç saat uyudu?",
                "Vardiyası kaç saatlik?",
                "Fazla mesai yaptı mı?"
            ],
            
            # D - ÖRGÜTSEL FAKTÖRLER
            "D1.1": [
                "Güvenlik liderliği kim tarafından gösteriliyor?",
                "Yönetim güvenliği önceliklendirir mi?",
                "Güvenlik hedefleri var mı?"
            ],
            "D3.1": [
                "Eğitim programının içeriği nedir?",
                "Eğitim kayıtları mevcut mu?",
                "Eğitim etkinliği ölçülüyor mu?"
            ],
            "D4.1": [
                "Neden prosedür hazırlanmamış?",
                "Risk değerlendirmesinde prosedür ihtiyacı görülmüş mü?",
                "Prosedür hazırlama planı var mı?"
            ],
            "D5.3": [
                "Risk değerlendirmesi yapıldı mı? Ne zaman?",
                "Risk değerlendirmesini kim yaptı?",
                "Değerlendirme sonrası aksiyonlar alındı mı?"
            ],
            "D6.1": [
                "Bakım planı mevcut mu?",
                "Bakım neden yapılmadı?",
                "Bakım için kaynak/bütçe var mı?"
            ]
        }
        
        questions = []
        for code in suspected_codes:
            if code in code_questions:
                for q in code_questions[code]:
                    questions.append({
                        "hsg245_code": code,
                        "question": q,
                        "code_description": self._get_code_description(code)
                    })
        
        return questions
    
    def _get_code_description(self, code: str) -> str:
        """HSG245 kodunun açıklamasını taxonomy'den çek"""
        # Basit parsing - gerçek uygulamada daha sofistike olabilir
        all_text = "\n".join(self.taxonomy.values())
        
        for line in all_text.split('\n'):
            if code in line:
                # Kod açıklamasını al
                parts = line.split('→')
                if len(parts) > 0:
                    return parts[0].replace(code, '').strip()
        
        return "Açıklama bulunamadı"
    
    def get_followup_questions(self, answer: str, category: str) -> list:
        """
        Verilen cevaba göre takip soruları üret (5-Why logic)
        
        Args:
            answer: Kullanıcının cevabı
            category: Soru kategorisi
            
        Returns:
            Takip soruları listesi
        """
        # Basit kural tabanlı takip soruları
        followup = []
        
        # Anahtar kelimelere göre takip soruları
        if "bilmiyordu" in answer.lower() or "haberdar değil" in answer.lower():
            followup.append({
                "question": "Neden bilmiyordu? Eğitim verilmemiş miydi?",
                "hsg245_link": "D3.1 (Yetersiz eğitim)",
                "why_level": 2
            })
            
        if "vardı" in answer.lower() and "kullanmadı" in answer.lower():
            followup.append({
                "question": "Neden kullanmadı? Rahatsızlık mı veriyordu?",
                "hsg245_link": "A3.2 (KKD kullanmama) → A3.6 (Rahatsız edici KKD)",
                "why_level": 2
            })
            
        if "arızalı" in answer.lower() or "bozuk" in answer.lower():
            followup.append({
                "question": "Arıza neden rapor edilmemişti?",
                "hsg245_link": "D2.3 (Raporlama eksikliği)",
                "why_level": 2
            })
            followup.append({
                "question": "Bakım neden yapılmamıştı?",
                "hsg245_link": "D6.1 (Bakım eksikliği)",
                "why_level": 2
            })
        
        return followup


# Test fonksiyonları
if __name__ == "__main__":
    print("=" * 80)
    print("QUESTION ENGINE - HSG245 Entegrasyonu Testi")
    print("=" * 80)
    
    engine = QuestionEngine()
    
    # Test 1: Eksik kategoriler için sorular
    print("\n[TEST 1] Eksik Kategoriler İçin Sorular\n")
    missing = ['prosedür', 'ekipman', 'eğitim']
    questions = engine.generate_questions_for_missing_categories(missing)
    
    for i, q in enumerate(questions, 1):
        required_mark = "🔴 ZORUNLU" if q["required"] else "⚪ OPSİYONEL"
        print(f"\n{i}. [{required_mark}] {q['category'].upper()}: {q['question']}")
        print(f"   📊 HSG245 Kodları: {q['hsg245_codes']}")
        print(f"   🔗 Bağlantı: {q['hsg245_link']}")
    
    # Test 2: Spesifik kod soruları
    print("\n" + "=" * 80)
    print("[TEST 2] HSG245 Kod Spesifik Sorular\n")
    suspected_codes = ['A1.1', 'D3.1', 'B2.1']
    code_questions = engine.get_code_specific_questions(suspected_codes)
    
    for i, q in enumerate(code_questions, 1):
        print(f"\n{i}. [Kod: {q['hsg245_code']}] {q['question']}")
        print(f"   📝 Kod: {q['code_description']}")
    
    # Test 3: Takip soruları
    print("\n" + "=" * 80)
    print("[TEST 3] Takip Soruları (5-Why)\n")
    
    test_answers = [
        ("Çalışan prosedürü bilmiyordu", "prosedür"),
        ("Ekipman arızalıydı ama kullandı", "ekipman"),
        ("KKD vardı ama kullanmadı", "ppe")
    ]
    
    for answer, category in test_answers:
        print(f"\n💬 Cevap: '{answer}'")
        followups = engine.get_followup_questions(answer, category)
        for fq in followups:
            print(f"  ❓ Takip: {fq['question']}")
            print(f"     🔗 {fq['hsg245_link']}")
            print(f"     📊 Why Seviyesi: {fq['why_level']}")
    
    print("\n" + "=" * 80)
    print("✅ Test tamamlandı!")
    print("=" * 80)
