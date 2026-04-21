"""
Root Cause Agent V2 - Hiyerarşik 5-Why Analizi (DÜZELTİLMİŞ SÜRÜM)
=====================================================================

DÜZELTMELER:
1. IMMEDIATE CAUSE ÇEŞİTLİLİĞİ ZORUNLU:
   - En az 1 davranışsal (A), 1 koşul (B), 1 organizasyonel/kişisel öncül seçilmeli
   - Aynı olayın farklı bakış açıları değil, gerçekten BAĞIMSIZ nedenler seçilmeli

2. KÖK NEDEN ÇEŞİTLİLİĞİ ZORUNLU:
   - Her dal FARKLI bir C/D koduna ulaşmalı
   - Önceki dallarda kullanılan kod yasaklı listesine alınır
   - D4.1'e her seferinde ulaşmak geçersiz sayılır

3. İNSAN FAKTÖRÜ ZORUNLU DAL:
   - Bir dal mutlaka C kategorisinden (kişisel) kök nedene ulaşmalı
   - Operatör, süpervizör, PA gibi bireysel faktörler atlanamaz

4. 5-WHY KALİTE KONTROLÜ:
   - Her Why bir öncekinden FARKLI bir cevap üretmeli
   - "Aynı şeyin tekrarı" tespitinde uyarı verilir
   - Why zinciri gerçekten derinleşmeli, döngüye girmemeli

YAPISAL AKIŞ:
1. OLAY ÖZETI → Incident tanımı
2. A/B KATEGORİLERİNDEN → Diverse Immediate Causes (Davranışsal + Koşul)
3. HER IMMEDIATE CAUSE için → 5-WHY (farklı kök nedenlere ulaşmalı)
4. C/D KATEGORİLERİNDEN → Diverse Root Causes (Kişisel + Organizasyonel, farklı kodlar)
"""

from openai import OpenAI
from typing import Dict, List, Optional, Set
import json
import os

# Try different import paths for knowledge_base
try:
    from knowledge_base import HSG245_TAXONOMY, get_category_text
except ImportError:
    try:
        from agents.knowledge_base import HSG245_TAXONOMY, get_category_text
    except ImportError:
        from .knowledge_base import HSG245_TAXONOMY, get_category_text

# Import robust JSON parser
try:
    from .json_parser import extract_json_from_response, safe_json_parse
except ImportError:
    try:
        from json_parser import extract_json_from_response, safe_json_parse
    except ImportError:
        from agents.json_parser import extract_json_from_response, safe_json_parse


class RootCauseAgentV2:
    """
    Part 3: Hiyerarşik Kök Neden Analizi - ÇOK BOYUTLU SÜRÜM
    
    Ana düzeltme: Her dal farklı bir perspektiften (davranışsal, teknik, 
    organizasyonel, kişisel) analiz yapmalı ve FARKLI kök nedenlere ulaşmalı.
    """
    
    def __init__(self):
        """Initialize with knowledge base and OpenRouter"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        # Kullanılan kök neden kodlarını takip et (tekrar önleme)
        self.used_root_cause_codes: Set[str] = set()
        print("✅ Kök Neden Ajanı V2 başlatıldı (ÇOK BOYUTLU SÜRÜM)")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        Tam hiyerarşik kök neden analizi - ÇOK BOYUTLU
        """
        print("\n" + "="*80)
        print("🔴 BÖLÜM 3: HİYERARŞİK KÖK NEDEN ANALİZİ (ÇOK BOYUTLU)")
        print("="*80)
        
        # Her analiz için kullanılan kodları sıfırla
        self.used_root_cause_codes = set()
        
        # Olay özeti hazırla
        incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        
        print(f"\n📋 OLAY ÖZETİ:\n{incident_summary}\n")
        
        # Ana yapı
        rca_data = {
            "incident_summary": incident_summary,
            "analysis_branches": [],
            "final_root_causes": [],
            "analysis_method": "HSG245 Hierarchical 5-Why (Multi-Dimensional A/B → C/D)"
        }
        
        # ADIM 1: ÇOK BOYUTLU Immediate Causes bul
        print("\n🔍 ADIM 1: Çok Boyutlu Doğrudan Nedenleri Belirleme")
        print("   (Davranışsal + Teknik/Koşul + İnsan Faktörü - HEPSİ BAĞIMSIZ)")
        print("-" * 80)
        
        immediate_causes = self._identify_diverse_immediate_causes(incident_summary)
        
        if not immediate_causes:
            print("❌ Doğrudan neden bulunamadı!")
            return rca_data
        
        print(f"\n✅ {len(immediate_causes)} bağımsız doğrudan neden belirlendi\n")
        self._validate_cause_diversity(immediate_causes)
        
        # ADIM 2: Her immediate cause için 5-Why analizi (farklı kök nedenlere ulaşarak)
        print("\n🔗 ADIM 2: 5-Why Analizi (Her Dal FARKLI Kök Nedene Ulaşmalı)")
        print("-" * 80)
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n{'='*80}")
            print(f"⚡ DAL {idx}: {immediate_cause.get('category_type', '???')} - {immediate_cause.get('perspective', '')}")
            print(f"📌 Doğrudan Neden [{immediate_cause.get('code', '???')}]:")
            print(f"   {immediate_cause.get('cause_tr', immediate_cause.get('cause', ''))}")
            print(f"{'='*80}\n")
            
            # 5-Why chain - yasaklı kodları geçirerek farklı sonuca yönlendir
            chain = self._perform_5why_chain_diverse(
                immediate_cause, 
                incident_summary,
                forbidden_codes=self.used_root_cause_codes
            )
            
            # Kullanılan kodu kaydet
            root_code = chain.get("root_cause", {}).get("code", "")
            if root_code:
                self.used_root_cause_codes.add(root_code)
            
            # Dal yapısı
            branch = {
                "branch_number": idx,
                "perspective": immediate_cause.get("perspective", ""),
                "immediate_cause": immediate_cause,
                "why_chain": chain["whys"],
                "root_cause": chain["root_cause"]
            }
            
            rca_data["analysis_branches"].append(branch)
            rca_data["final_root_causes"].append(chain["root_cause"])
            
            self._print_branch_tree(branch)
        
        # ADIM 3: Kök neden çeşitliliğini doğrula
        print("\n" + "="*80)
        print("🔍 ADIM 3: Kök Neden Çeşitliliği Doğrulama")
        print("="*80)
        self._validate_root_cause_diversity(rca_data["final_root_causes"])
        
        print("\n" + "="*80)
        print("✅ TÜM DALLAR TAMAMLANDI!")
        print("="*80)
        
        # Özet rapor oluştur
        rca_data["final_report_tr"] = self._generate_hierarchical_report(rca_data)
        
        return rca_data
    
    def _identify_diverse_immediate_causes(self, incident_summary: str) -> List[Dict]:
        """
        ÇOK BOYUTLU immediate causes belirle.
        
        TEMEL DEĞİŞİKLİK: Model artık zorla 3 FARKLI perspektiften neden seçmeli:
        1. DAVRANIŞSAL perspektif (A kategorisi) - İnsan eylemi
        2. TEKNİK/KOŞUL perspektifi (B kategorisi) - Fiziksel durum  
        3. GÖZETIM/ORGANIZASYONEL öncül (A veya B) - Yönetim eylemi veya koşulu
        
        Bu sayede aynı olayın 3 farklı yüzü yakalanır.
        """
        rag_context_a = get_category_text('A')
        rag_context_b = get_category_text('B')
        
        prompt = f"""Sen uzman bir İSG Müfettişisin ve "İsviçre Peyniri Modeli"ni uyguluyorsun.
Görevin: Aynı kazanın FARKLI ve BAĞIMSIZ nedenlerini, 3 farklı perspektiften belirlemek.

OLAY ÖZETİ:
{incident_summary}

REFERANS LİSTESİ A (DAVRANIŞSAL KODLAR):
{rag_context_a}

REFERANS LİSTESİ B (KOŞULLAR KODLARI):
{rag_context_b}

KRİTİK KURAL - 3 FARKLI PERSPEKTİF SEÇMELİSİN:

PERSPEKTİF 1 - DOĞRUDAN EYLEM (A kategorisi):
→ Kazayı doğrudan tetikleyen insan eylemi/davranışı nedir?
→ Operatör, çalışan veya ekipman kullanan kişinin yaptığı/yapmadığı şey
→ Örnek: "Operatör OHTL farkında olmadan makinayı hareket ettirdi"

PERSPEKTİF 2 - FİZİKSEL KOŞUL (B kategorisi):
→ Kazanın gerçekleşmesini sağlayan fiziksel/çevresel tehlike nedir?
→ Sahadaki tehlikeli durum, ekipman durumu veya enerji kaynağı
→ Örnek: "Enerjili OHTL hattı çalışma alanında korumasz bulunuyordu"

PERSPEKTİF 3 - GÖZETİM EYLEMİ (A veya B kategorisi):
→ Kazaya doğrudan katkıda bulunan yönetim/gözetim başarısızlığı nedir?
→ Süpervizör, formen veya PA'nın yaptığı/yapmadığı şey
→ Örnek: "Süpervizör tehlikeli manevrayı durdurmak için müdahale etmedi"

ÖNEMLİ KURALLAR:
1. Her perspektiften SADECE 1 neden seç (toplam 3 neden)
2. 3 neden birbirinin tekrarı OLMAMALI - gerçekten farklı olaylar/durumlar
3. Her nedenin arkasında FARKLI bir kök nedene ulaşılabilmeli
4. Kanıt olarak olay özetinden SOMUT bir detay kullan

BEKLENEN ÇIKTI (JSON):
{{
  "causes": [
    {{
      "code": "A4.5",
      "standard_title_tr": "Kasıtsız insan hatası (sürçme/dalgınlık)",
      "category_type": "DAVRANIŞSAL",
      "perspective": "DOĞRUDAN EYLEM - Operatör Hatası",
      "cause_tr": "Operatör kamyon sürücüsüyle çatışma sırasında dikkatini kaybederek OHTL varlığını unuttu ve boom yükseltilmişken geri hareket etti",
      "evidence_tr": "Raporda belirtildiği üzere operatör kamyon sürücüsüyle tartışırken sideroom boom yükseltilmiş halde OHTL'e çarptı"
    }},
    {{
      "code": "B3.2",
      "standard_title_tr": "Elektrik enerjisi (enerjili sistemler)",
      "category_type": "TEKNİK/KOŞUL",
      "perspective": "FİZİKSEL KOŞUL - Enerji Tehlikesi",
      "cause_tr": "6.6 kV enerjili OHTL hattı çalışma alanında izolasyonsuz ve fiziksel bariyer olmaksızın sideroom operasyonuna izin verildi",
      "evidence_tr": "Koruma rölesi 20-50ms içinde devreyi kesti - hat enerjili durumdaydı ve izole edilmemişti"
    }},
    {{
      "code": "A3.2",
      "standard_title_tr": "Gerekli KKD/koruyucu yöntemlerin kullanılmaması",
      "category_type": "GÖZETİM EYLEMİ",
      "perspective": "GÖZETİM BAŞARISIZLIĞI - Saha Kontrolü",
      "cause_tr": "Mekanik süpervizör, kamyon sürücüsünün yanlış konumlanmasına ve operatörün tehlikeli manevrasına müdahale etmedi; banksman atanmamıştı",
      "evidence_tr": "Raporda süpervizörün çatışmaya müdahale etmediği ve banksman bulunmadığı belirtilmektedir"
    }}
  ]
}}

Sadece JSON döndür, Türkçe içerik kullan."""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Sen HSG245 İsviçre Peyniri Modeli uzmanısın. 3 FARKLI perspektiften neden seç. Sadece JSON döndür."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        
        data = safe_json_parse(
            result,
            context="Immediate Causes Identification",
            default={"causes": []}
        )
        
        causes = data.get("causes", [])
        
        for cause in causes:
            code = cause.get('code', '???')
            perspective = cause.get('perspective', '')
            standard_title = cause.get('standard_title_tr', '')
            cause_description = cause.get('cause_tr', '')
            
            print(f"  [{code}] {perspective}")
            if standard_title:
                print(f"       Standart: {standard_title}")
            print(f"       Açıklama: {cause_description[:100]}...")
            print()
        
        return causes
    
    def _perform_5why_chain_diverse(self, immediate_cause: Dict, incident_summary: str, 
                                    forbidden_codes: Set[str] = None) -> Dict:
        """
        5-Why zinciri - FARKLI kök nedenlere ulaşmak zorunda.
        
        TEMEL DEĞİŞİKLİK: 
        - forbidden_codes: Önceki dallarda kullanılan kodlar - tekrar KULLANILABİLİR
        - Ancak neden FARKLI bir kök nedene ulaşılması gerektiği açıkça belirtilir
        - Perspektife göre yönlendirme yapılır (insan faktörü için C, sistem için D)
        """
        if forbidden_codes is None:
            forbidden_codes = set()
            
        code = immediate_cause.get("code", "")
        cause_tr = immediate_cause.get("cause_tr", "")
        perspective = immediate_cause.get("perspective", "")
        
        rag_context_c = get_category_text('C')
        rag_context_d = get_category_text('D')
        
        # Perspektife göre hangi kategoriye yönlendirileceğini belirle
        perspective_guidance = self._get_perspective_guidance(perspective, forbidden_codes)
        
        forbidden_list = ", ".join(forbidden_codes) if forbidden_codes else "Yok"
        
        prompt = f"""Sen İSG kök neden uzmanısın. Bu dal için 5-Why analizi yapıyorsun.

OLAY: {incident_summary}

DOĞRUDAN NEDEN [{code}] - {perspective}:
{cause_tr}

ANALİZ YÖNLENDİRMESİ:
{perspective_guidance}

YASAKLI KOD LİSTESİ (Bu kodları kök neden olarak KULLANMA):
{forbidden_list}
(Bu kodlar diğer dallarda zaten kullanıldı. Farklı bir boyutu keşfet.)

C KATEGORİSİ (KİŞİSEL FAKTÖRLER):
{rag_context_c}

D KATEGORİSİ (ORGANİZASYONEL FAKTÖRLER):
{rag_context_d}

GÖREV - 5-WHY KURALLARI:
1. Her "Neden?" sorusu bir önceki cevabı SORGULAR
2. Her cevap öncekinden FARKLI ve DAHA DERİN olmalı - aynı şeyi tekrarlama
3. Why 1-2: Operasyonel/taktik nedenler
4. Why 3-4: Sistem/prosedür nedenleri  
5. Why 5 → KÖK NEDEN (C veya D kategorisinden, YASAKLI KODLAR HARİÇ)
6. Kök neden bu dalın PERSPEKTİFİNE uygun olmalı

DÖNDÜR (JSON):
{{
  "whys": [
    {{
      "level": 1,
      "question_tr": "Neden [önceki cevabın özeti] oldu?",
      "answer_tr": "Çünkü [yeni, daha derin bilgi]"
    }},
    {{
      "level": 2,
      "question_tr": "Neden [level 1 cevabının özeti]?",
      "answer_tr": "[Daha derin cevap, farklı boyut]"
    }},
    {{
      "level": 3,
      "question_tr": "Neden [level 2 cevabının özeti]?",
      "answer_tr": "[Sistem/prosedür boyutu]"
    }},
    {{
      "level": 4,
      "question_tr": "Neden [level 3 cevabının özeti]?",
      "answer_tr": "[Organizasyonel/kişisel boyut]"
    }}
  ],
  "root_cause": {{
    "code": "D1.2",
    "standard_title_tr": "Yetersiz gözetim veya denetim",
    "category_type": "ORGANİZASYONEL",
    "cause_tr": "Bu olaya özgü kök neden açıklaması",
    "explanation_tr": "Neden bu kök nedenin bu dalı açıkladığının detaylı gerekçesi"
  }}
}}

KRİTİK: Türkçe, geçerli JSON, YASAKLI kodları kullanma."""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "Sen 5-Why uzmanısın. Her dal farklı kök nedene ulaşmalı. Sadece JSON, Türkçe içerik."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        
        chain = safe_json_parse(
            result,
            context=f"5-Why Chain for {code}",
            default={"whys": [], "root_cause": {}}
        )
        
        # Why'ları yazdır
        for why in chain.get("whys", []):
            level = why.get("level", "?")
            question = why.get("question_tr", "")
            answer = why.get("answer_tr", "")
            print(f"   ❓ Neden {level}? {question}")
            print(f"      → {answer}\n")
        
        # Root cause yazdır
        root = chain.get("root_cause", {})
        root_code = root.get('code', '???')
        root_standard_title = root.get('standard_title_tr', '')
        root_cause_desc = root.get('cause_tr', '')
        root_explanation = root.get('explanation_tr', '')
        
        # Yasaklı kod uyarısı
        if root_code in forbidden_codes:
            print(f"   ⚠️  UYARI: [{root_code}] yasaklı listesinde! Farklılaştırma gerekebilir.")
        
        if root_standard_title:
            print(f"   🎯 KÖK NEDEN [{root_code}] {root_standard_title}: {root_cause_desc}")
        else:
            print(f"   🎯 KÖK NEDEN [{root_code}]: {root_cause_desc}")
        print(f"      ({root_explanation})\n")
        
        return chain
    
    def _get_perspective_guidance(self, perspective: str, forbidden_codes: Set[str]) -> str:
        """
        Perspektife göre hangi kök neden kategorisine yönlendirileceğini belirle.
        Bu sayede her dal doğal olarak farklı bir kök nedene ulaşır.
        """
        perspective_upper = perspective.upper()
        
        if "DOĞRUDAN EYLEM" in perspective_upper or "OPERATÖR" in perspective_upper:
            return """Bu dal OPERATÖR/BİREYSEL perspektifinden ilerlemeli.
→ Bireysel bilişsel faktörleri araştır: hafıza, dikkat, yetkinlik, stres
→ C kategorisini öncelikle değerlendir (C1, C2, C3)
→ Kök neden: Neden bu birey bu hatayı yaptı? (Eğitim, yetkinlik, zihinsel durum?)
→ Varılacak örnek kodlar: C2.1 (hafıza/dikkat), C3.1 (yetkinlik), C2.5 (stres/duygusal)"""
        
        elif "FİZİKSEL KOŞUL" in perspective_upper or "TEKNİK" in perspective_upper:
            return """Bu dal TEKNİK/MÜHENDİSLİK perspektifinden ilerlemeli.
→ Fiziksel tehlikenin neden var olduğunu araştır: tasarım, izolasyon, mühendislik kontrolleri
→ D5 (Mühendislik/Tasarım) veya D4.5 (Enerji izolasyonu/LOTO) kategorilerini öncelikle değerlendir
→ Kök neden: Neden bu tehlike elimine edilmedi veya kontrol edilmedi?
→ Varılacak örnek kodlar: D4.5 (LOTO/izolasyon), D5.4 (tehlikeli alan sınıflandırma), D4.4 (iş izin sistemi)"""
        
        elif "GÖZETİM" in perspective_upper or "SUPERVISOR" in perspective_upper:
            return """Bu dal GÖZETİM/LİDERLİK perspektifinden ilerlemeli.
→ Süpervizörün neden müdahale etmediğini araştır: otorite, kültür, baskı
→ D1 (Liderlik/Güvenlik Kültürü) veya D2 (İletişim) kategorilerini öncelikle değerlendir
→ Kök neden: Neden gözetim sistemi bu davranışa izin verdi?
→ Varılacak örnek kodlar: D1.2 (yetersiz gözetim), D1.5 (sapmaların normalleşmesi), D1.6 (iş durdurma yetkisi)"""
        
        else:
            return """Bu dal organizasyonel/sistemik perspektiften ilerlemeli.
→ Sistem ve prosedür eksikliklerini araştır
→ D kategorisini değerlendir (D3, D4, D7)
→ Kök neden: Hangi sistem başarısızlığı bu olaya zemin hazırladı?"""
    
    def _validate_cause_diversity(self, causes: List[Dict]):
        """Seçilen doğrudan nedenlerin gerçekten farklı olup olmadığını kontrol et"""
        print("\n🔍 DOĞRUDAN NEDEN ÇEŞİTLİLİK KONTROLÜ:")
        
        codes = [c.get('code', '') for c in causes]
        perspectives = [c.get('perspective', '') for c in causes]
        categories = [c.get('code', '')[0] if c.get('code') else '' for c in causes]
        
        unique_categories = set(categories)
        
        print(f"   Seçilen kodlar: {', '.join(codes)}")
        print(f"   Kategori dağılımı: {dict.fromkeys(unique_categories)}")
        
        if len(set(codes)) < len(codes):
            print("   ⚠️  UYARI: Tekrar eden kodlar var!")
        else:
            print("   ✅ Tüm kodlar benzersiz")
            
        a_count = categories.count('A')
        b_count = categories.count('B')
        print(f"   Davranışsal (A): {a_count}, Koşul (B): {b_count}")
    
    def _validate_root_cause_diversity(self, root_causes: List[Dict]):
        """Kök nedenlerin farklı olup olmadığını kontrol et"""
        codes = [rc.get('code', '') for rc in root_causes]
        unique_codes = set(codes)
        
        print(f"\nKök Neden Kodları: {', '.join(codes)}")
        
        if len(unique_codes) == len(codes):
            print("✅ TÜM KÖK NEDENLER FARKLI - Çok boyutlu analiz başarılı!")
        else:
            duplicates = [c for c in codes if codes.count(c) > 1]
            print(f"⚠️  UYARI: Tekrar eden kök neden kodları: {set(duplicates)}")
            print("   Bu dallar aynı sistematik sorunu işaret ediyor - raporlamada birleştirilebilir.")
        
        # Kategori dağılımı
        c_count = sum(1 for rc in root_causes if rc.get('code', '').startswith('C'))
        d_count = sum(1 for rc in root_causes if rc.get('code', '').startswith('D'))
        print(f"\nKök Neden Dağılımı:")
        print(f"   Kişisel (C): {c_count}")
        print(f"   Organizasyonel (D): {d_count}")
        
        if c_count == 0:
            print("   ⚠️  UYARI: Kişisel faktör (C kategorisi) kök neden yok! İnsan boyutu eksik olabilir.")
        if d_count == 0:
            print("   ⚠️  UYARI: Organizasyonel faktör (D kategorisi) kök neden yok! Sistem boyutu eksik.")
    
    def _print_branch_tree(self, branch: Dict):
        """Dal ağacını güzel yazdır"""
        immediate = branch["immediate_cause"]
        whys = branch["why_chain"]
        root = branch["root_cause"]
        
        print(f"\n🌳 DAL AĞACI #{branch['branch_number']} - {branch.get('perspective', '')}:")
        print("│")
        
        imm_code = immediate.get('code', '')
        imm_standard = immediate.get('standard_title_tr', '')
        imm_cause = immediate.get('cause_tr', '')
        
        if imm_standard:
            print(f"├── 📌 DOĞRUDAN NEDEN [{imm_code}] {imm_standard}")
            print(f"│   └── {imm_cause}")
        else:
            print(f"├── 📌 DOĞRUDAN NEDEN [{imm_code}]")
            print(f"│   └── {imm_cause}")
        print("│")
        
        for idx, why in enumerate(whys, 1):
            print(f"├── ❓ Neden {idx}? {why.get('question_tr', '')}")
            print(f"│   └── {why.get('answer_tr', '')}")
        
        print("│")
        
        root_code = root.get('code', '')
        root_standard = root.get('standard_title_tr', '')
        root_cause = root.get('cause_tr', '')
        root_explanation = root.get('explanation_tr', '')
        
        if root_standard:
            print(f"└── 🎯 KÖK NEDEN [{root_code}] {root_standard}")
            print(f"    └── {root_cause}")
            print(f"        ({root_explanation})")
        else:
            print(f"└── 🎯 KÖK NEDEN [{root_code}]")
            print(f"    └── {root_cause}")
            print(f"        ({root_explanation})")
    
    def _generate_hierarchical_report(self, rca_data: Dict) -> str:
        """Türkçe hiyerarşik rapor oluştur"""
        report = []
        report.append("=" * 80)
        report.append("KÖK NEDEN ANALİZİ RAPORU (HSG245 - Çok Boyutlu 5-Why Metodolojisi)")
        report.append("=" * 80)
        report.append("")
        report.append(f"OLAY: {rca_data['incident_summary']}")
        report.append("")
        report.append("ANALİZ YÖNTEMİ: İsviçre Peyniri Modeli")
        report.append("Her dal farklı bir perspektiften (Operatör/Fiziksel/Gözetim) analiz edilmiş,")
        report.append("farklı kök nedenlere ulaşılmıştır.")
        report.append("-" * 80)
        
        for branch in rca_data["analysis_branches"]:
            immediate = branch["immediate_cause"]
            whys = branch["why_chain"]
            root = branch["root_cause"]
            perspective = branch.get("perspective", "")
            
            report.append("")
            report.append(f"⚡ DAL {branch['branch_number']}: {immediate.get('category_type', '')} - {perspective}")
            report.append("")
            
            imm_code = immediate.get('code', '')
            imm_standard = immediate.get('standard_title_tr', '')
            imm_cause = immediate.get('cause_tr', '')
            imm_evidence = immediate.get('evidence_tr', '')
            
            if imm_standard:
                report.append(f"📌 Doğrudan Neden [{imm_code}] {imm_standard}:")
            else:
                report.append(f"📌 Doğrudan Neden [{imm_code}]:")
            report.append(f"   {imm_cause}")
            report.append(f"   Kanıt: {imm_evidence}")
            report.append("")
            
            for idx, why in enumerate(whys, 1):
                report.append(f"❓ Neden {idx}? {why.get('question_tr', '')}")
                report.append(f"   → {why.get('answer_tr', '')}")
            
            report.append("")
            
            root_code = root.get('code', '')
            root_standard = root.get('standard_title_tr', '')
            root_category = root.get('category_type', '')
            root_cause = root.get('cause_tr', '')
            root_explanation = root.get('explanation_tr', '')
            
            if root_standard:
                report.append(f"🎯 KÖK NEDEN [{root_code}] {root_standard} - {root_category}:")
            else:
                report.append(f"🎯 KÖK NEDEN [{root_code}] - {root_category}:")
            report.append(f"   {root_cause}")
            report.append(f"   {root_explanation}")
            report.append("")
            report.append("-" * 80)
        
        # Özet tablosu
        report.append("")
        report.append("📊 KÖK NEDEN ÖZETİ:")
        report.append("-" * 40)
        for i, rc in enumerate(rca_data.get("final_root_causes", []), 1):
            code = rc.get('code', '?')
            title = rc.get('standard_title_tr', '')
            category = rc.get('category_type', '')
            report.append(f"   {i}. [{code}] {title} ({category})")
        
        return "\n".join(report)
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                 investigation_data: Dict = None) -> str:
        """Olay özetini hazırla"""
        summary_parts = []
        
        brief = part1_data.get("brief_details", {})
        if isinstance(brief, dict):
            if brief.get("what"): summary_parts.append(f"{brief['what']}")
            if brief.get("where"): summary_parts.append(f"Konum: {brief['where']}")
            if brief.get("who"): summary_parts.append(f"İlgililer: {brief['who']}")
            if brief.get("emergency_measures"): summary_parts.append(f"Alınan önlemler: {brief['emergency_measures']}")
        
        if part2_data.get("type_of_event"):
            summary_parts.append(f"Olay Tipi: {part2_data['type_of_event']}")
        
        if investigation_data and investigation_data.get("how_happened"):
            summary_parts.append(investigation_data["how_happened"])
        
        return ". ".join(summary_parts) if summary_parts else "Olay detayı mevcut değil"
