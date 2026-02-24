"""
Root Cause Agent V2 - Hiyerarşik 5-Why Analizi
================================================

YAPISAL AKIŞ:
1. OLAY ÖZETI → Incident tanımı
2. A/B KATEGORİLERİNDEN → Immediate Causes (Doğrudan Nedenler)
   - A: Davranışsal (Actions)
   - B: Koşullar (Conditions)
3. HER IMMEDIATE CAUSE için → 5-WHY ANALİZİ
   - Why 1
   - Why 2 (Underlying)
   - Why 3 (Underlying)
   - Why 4
   - Why 5 → ROOT CAUSE (C veya D kategorisinden)
4. C/D KATEGORİLERİNDEN → Root Causes
   - C: Kişisel Faktörler (Personal)
   - D: Organizasyonel Faktörler (Organizational)

ÇIKTI YAPISI:
🔴 OLAY (INCIDENT)
│
├───⚡ DAL 1: MEKANİK/FİZİKSEL (B Kategorisi - Conditions)
│   ├── 📌 Doğrudan Neden [KOD: B1.6]
│   ├── ❓ Neden 1?
│   ├── ❓ Neden 2?
│   ├── ❓ Neden 3?
│   └── 🎯 KÖK NEDEN [KOD: D6.1]
│
└───⚡ DAL 2: DAVRANIŞSAL (A Kategorisi - Actions)
    ├── 📌 Doğrudan Neden [KOD: A1.4]
    ├── ❓ Neden 1?
    ├── ❓ Neden 2?
    ├── ❓ Neden 3?
    └── 🎯 KÖK NEDEN [KOD: D1.4]
"""

from openai import OpenAI
from typing import Dict, List, Optional
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
    Part 3: Hiyerarşik Kök Neden Analizi
    A/B → 5-Why → C/D yapısı
    """
    
    def __init__(self):
        """Initialize with knowledge base and OpenRouter"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print("✅ Kök Neden Ajanı V2 başlatıldı (knowledge_base)")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        Tam hiyerarşik kök neden analizi
        """
        print("\n" + "="*80)
        print("🔴 BÖLÜM 3: HİYERARŞİK KÖK NEDEN ANALİZİ")
        print("="*80)
        
        # Olay özeti hazırla
        incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        
        print(f"\n📋 OLAY ÖZETİ:\n{incident_summary}\n")
        
        # Ana yapı
        rca_data = {
            "incident_summary": incident_summary,
            "analysis_branches": [],  # Her dal bir immediate cause + 5-why chain
            "final_root_causes": [],
            "analysis_method": "HSG245 Hierarchical 5-Why (A/B → C/D)"
        }
        
        # ADIM 1: A/B kategorilerinden Immediate Causes bul
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme (A/B Kategorileri)")
        print("-" * 80)
        
        immediate_causes = self._identify_immediate_causes_with_codes(incident_summary)
        
        if not immediate_causes:
            print("❌ Doğrudan neden bulunamadı!")
            return rca_data
        
        print(f"✅ {len(immediate_causes)} doğrudan neden belirlendi\n")
        
        # ADIM 2: Her immediate cause için 5-Why analizi
        print("\n🔗 ADIM 2: 5-Why Analizi (Her Dal için)")
        print("-" * 80)
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n{'='*80}")
            print(f"⚡ DAL {idx}: {immediate_cause.get('category_type', '???')}")
            print(f"📌 Doğrudan Neden [{immediate_cause.get('code', '???')}]:")
            print(f"   {immediate_cause.get('cause_tr', immediate_cause.get('cause', ''))}")
            print(f"{'='*80}\n")
            
            # 5-Why chain oluştur
            chain = self._perform_5why_chain(immediate_cause, incident_summary)
            
            # Dal yapısı
            branch = {
                "branch_number": idx,
                "immediate_cause": immediate_cause,
                "why_chain": chain["whys"],
                "root_cause": chain["root_cause"]
            }
            
            rca_data["analysis_branches"].append(branch)
            rca_data["final_root_causes"].append(chain["root_cause"])
            
            self._print_branch_tree(branch)
        
        print("\n" + "="*80)
        print("✅ TÜM DALLAR TAMAMLANDI!")
        print("="*80)
        
        # Özet rapor oluştur
        rca_data["final_report_tr"] = self._generate_hierarchical_report(rca_data)
        
        return rca_data
    
    def _identify_immediate_causes_with_codes(self, incident_summary: str) -> List[Dict]:
        """
        A/B kategorilerinden immediate causes bul (RAG kullanarak veya hardcoded)
        """
        # A ve B kategorilerini knowledge_base'den al
        rag_context_a = get_category_text('A')
        rag_context_b = get_category_text('B')
        
        prompt = f"""
Sen uzman bir İSG Müfettişisin. Görevin, aşağıdaki iş kazası raporunu analiz etmek ve HSG245 standardına göre "Doğrudan Nedenleri" (Immediate Causes) belirlemektir.

GİRDİLER:
OLAY ÖZETİ:
{incident_summary}

REFERANS LİSTESİ A (DAVRANIŞSAL KODLAR):
{rag_context_a}

REFERANS LİSTESİ B (KOŞULLAR KODLARI):
{rag_context_b}

KRİTİK KURALLAR:
1. FİLTRELEME: Sadece kazayı doğrudan tetikleyen EN BASKIN nedenleri seç. Dolaylı faktörleri (örn: hava kapalıydı ama kaza içeride olduysa) ele.
2. LİMİT: Maksimum 3 (ÜÇ) adet en kritik nedeni belirle.
3. SIRALAMA: En kritikten aza doğru sırala.
4. FORMAT: Sadece saf JSON çıktısı ver. Markdown (```json) etiketi KULLANMA.

ALAN TANIMLARI (Buna Uy):
- "code": Referans listesinden seçtiğin kod (Örn: A1.4).
- "standard_title_tr": Referans listesinde o kodun karşısında yazan STANDART BAŞLIK (Değiştirme, birebir al).
- "cause_tr": Olay özelindeki açıklama. (Örn: Operatör yetkisi olmadığı halde panoyu açtı).
- "evidence_tr": Olay özetinden bu kararı destekleyen SOMUT KANIT veya ALINTI.

BEKLENEN ÇIKTI (JSON):
{{
  "causes": [
    {{
      "code": "A1.4",
      "standard_title_tr": "Yetkisiz faaliyet / değişiklik / devre dışı bırakma",
      "category_type": "DAVRANIŞSAL",
      "cause_tr": "Operatör yetkisi olmadığı halde makineye müdahale etti",
      "evidence_tr": "Raporda 'Operatör bakımcıyı beklemeden kapağı açtı' ifadesi geçmektedir."
    }}
  ]
}}
"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-sonnet-4.5",
            temperature=0.2,
            messages=[
                {
                    "role": "system", 
                    "content": [
                        {
                            "type": "text",
                            "text": "Sen HSG245 uzmanısın. Sadece JSON döndür, Türkçe içerik kullan.",
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                },
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "anthropic-version": "2023-06-01"
            }
        )
        
        result = response.choices[0].message.content.strip()
        
        # Use robust JSON parser
        data = safe_json_parse(
            result,
            context="Immediate Causes Identification",
            default={"causes": []}
        )
        
        causes = data.get("causes", [])
        
        for cause in causes:
            code = cause.get('code', '???')
            standard_title = cause.get('standard_title_tr', '')
            cause_description = cause.get('cause_tr', '')
            
            if standard_title:
                print(f"  [{code}] {standard_title}: {cause_description}")
            else:
                print(f"  [{code}] {cause_description}")
        
        return causes
    
    def _perform_5why_chain(self, immediate_cause: Dict, incident_summary: str) -> Dict:
        """
        Bir immediate cause için 5-Why zinciri oluştur
        Son Why → C/D kategorisinden root cause
        """
        code = immediate_cause.get("code", "")
        cause_tr = immediate_cause.get("cause_tr", "")
        
        # C ve D kategorilerini knowledge_base'den al
        rag_context_c = get_category_text('C')
        rag_context_d = get_category_text('D')
        
        prompt = f"""Sen İSG kök neden uzmanısın. 5-Why analizi yapıyorsun.

OLAY: {incident_summary}

DOĞRUDAN NEDEN [{code}]:
{cause_tr}

C KATEGORİSİ (KİŞİSEL FAKTÖRLER - ROOT CAUSES):
{rag_context_c}

D KATEGORİSİ (ORGANİZASYONEL FAKTÖRLER - ROOT CAUSES):
{rag_context_d}

GÖREV:
1. Bu doğrudan neden için 5-Why analizi yap
2. Why 1 ve Why 2 → Underlying causes (ara nedenler)
3. Why 3 ve Why 4 → Daha derin ara nedenler
4. Why 5 → ROOT CAUSE (C veya D kategorisinden seç, kod belirle)
5. Root cause için HSG245 tablosundaki standart Türkçe başlığını "standard_title_tr" alanına ekle

ÖNEMLİ:
- "standard_title_tr" alanı, C/D kategorisinden seçtiğin kodun orijinal HSG245 Türkçe başlığı olmalı
- "cause_tr" alanı bu olaya özgü açıklama olmalı

DÖNDÜR (JSON):
{{
  "whys": [
    {{
      "level": 1,
      "question_tr": "Neden güvenlik switch'i baypas edilmişti?",
      "answer_tr": "Switch arızalıydı ve üretim durmasın diye kısa devre yapıldı"
    }},
    {{
      "level": 2,
      "question_tr": "Neden yenisiyle değiştirilmedi?",
      "answer_tr": "Stokta yedek parça yoktu"
    }},
    {{
      "level": 3,
      "question_tr": "Neden yedek parça yoktu?",
      "answer_tr": "Kritik yedek parçaların takibi yapılmıyordu"
    }},
    {{
      "level": 4,
      "question_tr": "Neden takip yapılmıyordu?",
      "answer_tr": "Bakım planlaması yoktu ve envanter yönetimi eksikti"
    }}
  ],
  "root_cause": {{
    "code": "D6.1",
    "standard_title_tr": "Bakım sistemlerinin yetersizliği",
    "category_type": "ORGANİZASYONEL",
    "cause_tr": "Yetersiz Bakım Stratejisi ve Envanter Yönetimi",
    "explanation_tr": "Bakım planlaması yapılmamış, kritik parça stoku takip edilmiyor"
  }}
}}

KRİTİK: Tüm içerik %100 TÜRKÇE. Geçerli JSON döndür."""

        response = self.client.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Sen 5-Why uzmanısın. Sadece JSON, Türkçe içerik.",
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                },
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "anthropic-version": "2023-06-01"
            }
        )
        
        result = response.choices[0].message.content.strip()
        
        # Use robust JSON parser
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
        
        if root_standard_title:
            print(f"   🎯 KÖK NEDEN [{root_code}] {root_standard_title}: {root_cause_desc}")
        else:
            print(f"   🎯 KÖK NEDEN [{root_code}]: {root_cause_desc}")
        print(f"      ({root_explanation})\n")
        
        return chain
    
    def _print_branch_tree(self, branch: Dict):
        """Dal ağacını güzel yazdır"""
        immediate = branch["immediate_cause"]
        whys = branch["why_chain"]
        root = branch["root_cause"]
        
        print(f"\n🌳 DAL AĞACI #{branch['branch_number']}:")
        print("│")
        
        # Immediate cause with standard title
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
        
        # Root cause with standard title
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
        report.append("KÖK NEDEN ANALİZİ RAPORU (HSG245 - 5 Why Metodolojisi)")
        report.append("=" * 80)
        report.append("")
        report.append(f"OLAY: {rca_data['incident_summary']}")
        report.append("")
        report.append("-" * 80)
        
        for branch in rca_data["analysis_branches"]:
            immediate = branch["immediate_cause"]
            whys = branch["why_chain"]
            root = branch["root_cause"]
            
            report.append("")
            report.append(f"⚡ DAL {branch['branch_number']}: {immediate.get('category_type', '')}")
            report.append("")
            
            # Immediate cause with standard title
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
            
            # Root cause with standard title
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
        
        return "\n".join(report)
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                  investigation_data: Dict = None) -> str:
        """Olay özetini hazırla"""
        summary_parts = []
        
        # Part 1'den bilgiler
        brief = part1_data.get("brief_details", {})
        if isinstance(brief, dict):
            if brief.get("what"): summary_parts.append(f"{brief['what']}")
            if brief.get("where"): summary_parts.append(f"Konum: {brief['where']}")
        
        # Part 2'den bilgiler
        if part2_data.get("type_of_event"):
            summary_parts.append(f"Olay Tipi: {part2_data['type_of_event']}")
        
        # Investigation data
        if investigation_data and investigation_data.get("how_happened"):
            summary_parts.append(investigation_data["how_happened"])
        
        return ". ".join(summary_parts) if summary_parts else "Olay detayı mevcut değil"
