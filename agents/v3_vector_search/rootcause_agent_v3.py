"""
Root Cause Agent V3 - MongoDB Vector Search Entegrasyonu
=========================================================
V2'nin tüm özellikleri + Hibrit knowledge base (dictionary + vector)

DEĞİŞİKLİKLER (V2 → V3):
─────────────────────────────────────────────
✅ V2'nin tüm özellikleri korundu
➕ HybridKnowledgeBase kullanımı
➕ Semantik benzerlik bazlı kod önceliklendirme
➕ .env ile vector search açma/kapama (USE_VECTOR_SEARCH)

KULLANIM:
─────────────────────────────────────────────
# .env
USE_VECTOR_SEARCH=false  → V2 gibi çalışır (dictionary only)
USE_VECTOR_SEARCH=true   → Vector search aktif (semantik)

ORJI İNAL KOD:
─────────────────────────────────────────────
agents/rootcause_agent_v2.py AYNEN KORUNMUŞTUR.
Bu dosya sadece test için agents/v3_vector_search/ klasöründedir.
"""

from openai import OpenAI
from typing import Dict, List, Optional
import os
import sys
import importlib.util
from pathlib import Path

_agents_dir = Path(__file__).resolve().parent.parent
_mc_path = _agents_dir / "model_constants.py"
_spec = importlib.util.spec_from_file_location("agents_model_constants", _mc_path)
_mc = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mc)
OPENROUTER_DEFAULT_CHAT_MODEL = _mc.OPENROUTER_DEFAULT_CHAT_MODEL

# V3: Hibrit knowledge base import
try:
    from knowledge_base_vector_v3 import HybridKnowledgeBase
    USE_HYBRID = True
except ImportError:
    # Fallback: Orijinal knowledge_base.py
    try:
        # V3 klasöründen parent'a bak
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from knowledge_base import HSG245_TAXONOMY, get_category_text
        USE_HYBRID = False
    except ImportError:
        try:
            from agents.knowledge_base import HSG245_TAXONOMY, get_category_text
            USE_HYBRID = False
        except ImportError:
            from ..knowledge_base import HSG245_TAXONOMY, get_category_text
            USE_HYBRID = False

# Import robust JSON parser
try:
    from json_parser import extract_json_from_response, safe_json_parse
except ImportError:
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from json_parser import extract_json_from_response, safe_json_parse
    except ImportError:
        from agents.json_parser import extract_json_from_response, safe_json_parse


class RootCauseAgentV3:
    """
    Part 3: Hiyerarşik Kök Neden Analizi (V3 - Vector Search)
    A/B → 5-Why → C/D yapısı + Semantik kod önceliklendirme
    """

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # V3: Hibrit knowledge base
        if USE_HYBRID:
            try:
                self.kb = HybridKnowledgeBase()
                print("✅ Kök Neden Ajanı V3 başlatıldı (Hibrit: Dictionary + Vector)")
            except Exception as e:
                print(f"⚠️  Hibrit KB başarısız, fallback: {e}")
                self.kb = None
                print("✅ Kök Neden Ajanı V3 başlatıldı (Dictionary only)")
        else:
            self.kb = None
            print("✅ Kök Neden Ajanı V3 başlatıldı (Dictionary only - fallback)")

    # ─────────────────────────────────────────────────────────────────────────
    # ANA GİRİŞ NOKTASI
    # ─────────────────────────────────────────────────────────────────────────

    def analyze_root_causes(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None
    ) -> Dict:
        """Tam hiyerarşik kök neden analizi (V3 - Vector Enhanced)"""

        print("\n" + "=" * 80)
        print("🔴 BÖLÜM 3: HİYERARŞİK KÖK NEDEN ANALİZİ (V3 - Vector Search)")
        print("=" * 80)

        incident_summary = self._prepare_incident_summary(
            part1_data, part2_data, investigation_data
        )

        # HITL cevapları varsa özete ekle
        incident_summary = self._append_hitl_answers(incident_summary, investigation_data)

        print(f"\n📋 OLAY ÖZETİ (ilk 300 karakter):\n{incident_summary[:300]}...\n")

        rca_data = {
            "incident_summary": incident_summary,
            "analysis_branches": [],
            "final_root_causes": [],
            "analysis_method": "HSG245 Hierarchical 5-Why (V3 - Vector Enhanced)"
        }

        # ADIM 1: Immediate Causes
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme (A/B Kategorileri)")
        print("-" * 80)
        immediate_causes = self._identify_immediate_causes_with_codes(incident_summary)

        if not immediate_causes:
            print("❌ Doğrudan neden bulunamadı!")
            return rca_data

        print(f"✅ {len(immediate_causes)} doğrudan neden belirlendi\n")

        # ADIM 2: 5-Why zinciri
        print("\n🔗 ADIM 2: 5-Why Analizi (Her Dal için)")
        print("-" * 80)

        used_root_codes: List[str] = []

        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n{'=' * 80}")
            print(f"⚡ DAL {idx}: {immediate_cause.get('category_type', '???')}")
            print(f"📌 Doğrudan Neden [{immediate_cause.get('code', '???')}]:")
            print(f"   {immediate_cause.get('cause_tr', '')}")
            print(f"{'=' * 80}\n")

            chain = self._perform_5why_chain(
                immediate_cause,
                incident_summary,
                used_root_codes=used_root_codes
            )

            root_code = chain.get("root_cause", {}).get("code")
            if root_code:
                used_root_codes.append(root_code)

            branch = {
                "branch_number": idx,
                "immediate_cause": immediate_cause,
                "why_chain": chain.get("whys", []),
                "root_cause": chain.get("root_cause", {})
            }
            rca_data["analysis_branches"].append(branch)
            rca_data["final_root_causes"].append(chain.get("root_cause", {}))

            self._print_branch_tree(branch)

        print("\n" + "=" * 80)
        print("✅ TÜM DALLAR TAMAMLANDI!")
        print("=" * 80)

        rca_data["final_report_tr"] = self._generate_hierarchical_report(rca_data)
        return rca_data

    # ─────────────────────────────────────────────────────────────────────────
    # ADIM 1 — DOĞRUDAN NEDENLER (A / B KATEGORİLERİ)
    # ─────────────────────────────────────────────────────────────────────────

    def _identify_immediate_causes_with_codes(self, incident_summary: str) -> List[Dict]:
        """A/B kategorilerinden immediate causes bul (V3: Aynı, vector search burada kullanılmıyor)"""

        # V3: A/B için vector search kullanmıyoruz (sadece C/D için)
        # Fallback: Orijinal knowledge_base.py
        if USE_HYBRID and self.kb:
            rag_context_a = self.kb.get_category('A') if hasattr(self.kb, 'get_category') else get_category_text('A')
            rag_context_b = self.kb.get_category('B') if hasattr(self.kb, 'get_category') else get_category_text('B')
        else:
            rag_context_a = get_category_text('A')
            rag_context_b = get_category_text('B')

        prompt = f"""Sen uzman bir İSG Müfettişisin. Görevin, aşağıdaki iş kazası / çevre olayı raporunu
analiz etmek ve HSG245 standardına göre "Doğrudan Nedenleri" (Immediate Causes) belirlemektir.

GİRDİLER:

OLAY RAPORU (TAMAMI):
{incident_summary}

REFERANS LİSTESİ A (DAVRANIŞSAL KODLAR):
{rag_context_a}

REFERANS LİSTESİ B (KOŞULLAR KODLARI):
{rag_context_b}

─────────────────────────────────────────────
KRİTİK KURALLAR:
─────────────────────────────────────────────

1. SADECE RAPORDA YAZANLARI KULLAN
   Raporda açıkça geçen olgulara dayan. Raporda olmayan ekipman, kişi veya senaryoyu
   ASLA ekleme. Kafadan senaryo üretme.

2. FİLTRELEME
   Olayı DOĞRUDAN tetikleyen, olay anında gerçekleşen nedenleri seç.
   Dolaylı faktörleri (eğitim eksikliği, risk değerlendirmesi vb.) SEÇME —
   bunlar root cause kategorisine aittir.

3. LİMİT
   Maksimum 3 (ÜÇ) adet en kritik neden. Zorla doldurma.

4. ÇEŞİTLİLİK
   Mümkünse hem A (davranış) hem B (koşul) kategorisinden neden seç.

5. SPESİFİKLİK
   "Risk değerlendirmesi eksik", "eğitim yetersiz" gibi genel ifadeler
   DOĞRUDAN NEDEN DEĞİLDİR. Rapordaki somut, gözlemlenebilir olay veya
   koşulu kodla.

6. FORMAT
   Sadece saf JSON. Markdown etiketi (```json) KULLANMA.

─────────────────────────────────────────────
ALAN TANIMLARI:
─────────────────────────────────────────────
- "code"             : Referans listesinden uygun kod (örn: B2.1)
- "standard_title_tr": O kodun referans listesindeki STANDART BAŞLIĞI (birebir al)
- "category_type"    : "DAVRANIŞSAL" veya "KOŞUL"
- "cause_tr"         : Bu olaya özgü somut açıklama
- "evidence_tr"      : Olay raporundan bu kararı destekleyen SOMUT KANIT

─────────────────────────────────────────────
BEKLENEN ÇIKTI (JSON ŞEMASI):
─────────────────────────────────────────────
{{
  "causes": [
    {{
      "code": "<A veya B kategorisinden uygun kod>",
      "standard_title_tr": "<referans listesindeki orijinal Türkçe başlık>",
      "category_type": "<DAVRANIŞSAL veya KOŞUL>",
      "cause_tr": "<bu olaya özgü somut açıklama>",
      "evidence_tr": "<olay raporundan alınan somut kanıt>"
    }}
  ]
}}
"""

        response = self.client.chat.completions.create(
            model=OPENROUTER_DEFAULT_CHAT_MODEL,
            temperature=0.4,
            max_tokens=4000,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Sen HSG245 uzmanısın. Sadece JSON döndür, Türkçe içerik kullan. "
                                "Raporda olmayan senaryoları ASLA ekleme. "
                                "Genel/jenerik kodlardan kaçın; olaya özgü, spesifik kodları seç."
                            ),
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                },
                {"role": "user", "content": prompt}
            ],
            extra_headers={"anthropic-version": "2023-06-01"}
        )

        result = response.choices[0].message.content.strip()
        data = safe_json_parse(
            result,
            context="Immediate Causes Identification (V3)",
            default={"causes": []}
        )
        causes = data.get("causes", [])

        for cause in causes:
            code           = cause.get('code', '???')
            standard_title = cause.get('standard_title_tr', '')
            cause_desc     = cause.get('cause_tr', '')
            if standard_title:
                print(f"  [{code}] {standard_title}: {cause_desc}")
            else:
                print(f"  [{code}] {cause_desc}")

        return causes

    # ─────────────────────────────────────────────────────────────────────────
    # ADIM 2 — 5-WHY ZİNCİRİ (V3: VECTOR SEARCH KULLANIMI)
    # ─────────────────────────────────────────────────────────────────────────

    def _perform_5why_chain(
        self,
        immediate_cause: Dict,
        incident_summary: str,
        used_root_codes: List[str] = None
    ) -> Dict:
        """Bir immediate cause için 5-Why zinciri oluştur (V3 - Vector Enhanced)"""

        if used_root_codes is None:
            used_root_codes = []

        code     = immediate_cause.get("code", "")
        cause_tr = immediate_cause.get("cause_tr", "")

        # V3: Hibrit knowledge base kullanımı (vector search burada devreye girer)
        if USE_HYBRID and self.kb:
            print("  🔍 Vector search ile C/D kategorileri getiriliyor...")
            rag_context_c = self.kb.get_relevant_codes(
                incident_summary=incident_summary,
                category='C',
                top_k=5
            )
            rag_context_d = self.kb.get_relevant_codes(
                incident_summary=incident_summary,
                category='D',
                top_k=5
            )
        else:
            # Fallback: Orijinal dictionary
            rag_context_c = get_category_text('C')
            rag_context_d = get_category_text('D')

        if used_root_codes:
            banned_codes_str = (
                "YASAK KODLAR (önceki dallarda zaten seçildi, ROOT CAUSE olarak SEÇME):\n"
                + ", ".join(used_root_codes)
                + "\nFarklı, daha spesifik bir kod bul."
            )
        else:
            banned_codes_str = "Henüz kullanılmış kod yok."

        prompt = f"""Sen İSG kök neden uzmanısın. 5-Why analizi yapıyorsun.

OLAY RAPORU (TAMAMI):
{incident_summary}

DOĞRUDAN NEDEN [{code}]:
{cause_tr}

C KATEGORİSİ (KİŞİSEL FAKTÖRLER - ROOT CAUSES):
{rag_context_c}

D KATEGORİSİ (ORGANİZASYONEL FAKTÖRLER - ROOT CAUSES):
{rag_context_d}

─────────────────────────────────────────────
GÖREV:
─────────────────────────────────────────────

Bu doğrudan neden için mantıksal bir 5-Why zinciri kur:
  - Why 1 ve Why 2 → Doğrudan nedeni tetikleyen ara faktörler
  - Why 3 ve Why 4 → Daha derin sistemik faktörler
  - Why 5 → Root Cause (C veya D kategorisinden KOD ile)

─────────────────────────────────────────────
KRİTİK KURALLAR:
─────────────────────────────────────────────

A) SADECE RAPORDA YAZANLARA DAYAN
   Raporda geçmeyen ekipman, kişi, sistem veya senaryo EKLEME.
   Her "neden" sorusu ve cevabı rapordaki gerçek bulgulara dayanmalı.

B) {banned_codes_str}

C) SPESİFİKLİK KURALI
   "Risk değerlendirmesi eksikliği" (D1.x), "eğitim eksikliği" (D2.x) gibi
   kodlar HER KAZAYA uygulanabilecek jenerik kodlardır.
   Bu olay için DAHA SPESİFİK bir root cause varsa onu seç.
   Genel kodları ancak başka uygun kod yoksa kullan.

D) ZİNCİR TUTARLILIĞI
   Root cause, 5-Why zincirinin mantıksal sonucu olmalı.
   Zincirsiz, "havadan" bir root cause atama.

E) SEMANTİK ÖNCELİK (V3 YENİ)
   Yukarıdaki C/D listelerinde "🎯 SEMANTİK OLARAK EN YAKIN KODLAR" başlığı
   altında bu olaya en uygun kodlar vurgulanmıştır. Bu kodlara öncelik ver.
   Ancak başka bir kod daha uygunsa onu seç.

─────────────────────────────────────────────
DÖNDÜR (JSON ŞEMASI):
─────────────────────────────────────────────
{{
  "whys": [
    {{"level": 1, "question_tr": "<neden sorusu>", "answer_tr": "<cevap>"}},
    {{"level": 2, "question_tr": "<neden sorusu>", "answer_tr": "<cevap>"}},
    {{"level": 3, "question_tr": "<neden sorusu>", "answer_tr": "<cevap>"}},
    {{"level": 4, "question_tr": "<neden sorusu>", "answer_tr": "<cevap>"}}
  ],
  "root_cause": {{
    "code": "<C veya D kategorisinden uygun kod>",
    "standard_title_tr": "<HSG245 orijinal Türkçe başlık>",
    "category_type": "<KİŞİSEL veya ORGANİZASYONEL>",
    "cause_tr": "<bu olaya özgü kök neden açıklaması>",
    "explanation_tr": "<neden bu kod seçildi, 5-why zinciriyle bağlantısı>"
  }}
}}

KRİTİK: Tüm içerik %100 TÜRKÇE. Geçerli JSON döndür. Markdown etiketi kullanma."""

        response = self.client.chat.completions.create(
            model=OPENROUTER_DEFAULT_CHAT_MODEL,
            temperature=0.6,
            max_tokens=4000,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Sen 5-Why uzmanısın. Sadece JSON, Türkçe içerik. "
                                "Her kaza için özgün, spesifik kök nedenler üret. "
                                "Raporda olmayan senaryoları ASLA ekleme. "
                                "Jenerik/genel kodlardan kaçın. "
                                "Semantik benzerlik skorlarına dikkat et."
                            ),
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                },
                {"role": "user", "content": prompt}
            ],
            extra_headers={"anthropic-version": "2023-06-01"}
        )

        result = response.choices[0].message.content.strip()
        chain = safe_json_parse(
            result,
            context=f"5-Why Chain for {code} (V3)",
            default={"whys": [], "root_cause": {}}
        )

        for why in chain.get("whys", []):
            level    = why.get("level", "?")
            question = why.get("question_tr", "")
            answer   = why.get("answer_tr", "")
            print(f"  ❓ Neden {level}? {question}")
            print(f"     → {answer}\n")

        root            = chain.get("root_cause", {})
        root_code       = root.get('code', '???')
        root_standard   = root.get('standard_title_tr', '')
        root_cause_desc = root.get('cause_tr', '')
        root_explanation = root.get('explanation_tr', '')

        if root_standard:
            print(f"  🎯 KÖK NEDEN [{root_code}] {root_standard}: {root_cause_desc}")
        else:
            print(f"  🎯 KÖK NEDEN [{root_code}]: {root_cause_desc}")
        print(f"     ({root_explanation})\n")

        return chain

    # ─────────────────────────────────────────────────────────────────────────
    # YARDIMCI — DAL AĞACI (V2'den aynı)
    # ─────────────────────────────────────────────────────────────────────────

    def _print_branch_tree(self, branch: Dict):
        immediate = branch["immediate_cause"]
        whys      = branch.get("why_chain", [])
        root      = branch.get("root_cause", {})

        print(f"\n🌳 DAL AĞACI #{branch['branch_number']}:")
        print("│")

        imm_code     = immediate.get('code', '')
        imm_standard = immediate.get('standard_title_tr', '')
        imm_cause    = immediate.get('cause_tr', '')
        imm_evidence = immediate.get('evidence_tr', '')

        if imm_standard:
            print(f"├── 📌 DOĞRUDAN NEDEN [{imm_code}] {imm_standard}")
            print(f"│      └── {imm_cause}")
        else:
            print(f"├── 📌 DOĞRUDAN NEDEN [{imm_code}]")
            print(f"│      └── {imm_cause}")

        if imm_evidence:
            print(f"│      📎 Kanıt: {imm_evidence}")
        print("│")

        for idx, why in enumerate(whys, 1):
            print(f"├── ❓ Neden {idx}? {why.get('question_tr', '')}")
            print(f"│      └── {why.get('answer_tr', '')}")
            print("│")

        root_code        = root.get('code', '')
        root_standard    = root.get('standard_title_tr', '')
        root_cause       = root.get('cause_tr', '')
        root_explanation = root.get('explanation_tr', '')

        if root_standard:
            print(f"└── 🎯 KÖK NEDEN [{root_code}] {root_standard}")
            print(f"       └── {root_cause}")
        else:
            print(f"└── 🎯 KÖK NEDEN [{root_code}]")
            print(f"       └── {root_cause}")

        if root_explanation:
            print(f"       💡 {root_explanation}")

    # ─────────────────────────────────────────────────────────────────────────
    # YARDIMCI — HİYERARŞİK RAPOR (V2'den aynı)
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_hierarchical_report(self, rca_data: Dict) -> str:
        report = []
        report.append("=" * 80)
        report.append("KÖK NEDEN ANALİZİ RAPORU (HSG245 - 5 Why Metodolojisi - V3)")
        report.append("=" * 80)
        report.append("")
        report.append(f"OLAY: {rca_data['incident_summary'][:500]}...")
        report.append("")
        report.append("-" * 80)

        for branch in rca_data["analysis_branches"]:
            immediate = branch["immediate_cause"]
            whys      = branch.get("why_chain", [])
            root      = branch.get("root_cause", {})

            report.append("")
            report.append(f"⚡ DAL {branch['branch_number']}: {immediate.get('category_type', '')}")
            report.append("")

            imm_code     = immediate.get('code', '')
            imm_standard = immediate.get('standard_title_tr', '')
            imm_cause    = immediate.get('cause_tr', '')
            imm_evidence = immediate.get('evidence_tr', '')

            if imm_standard:
                report.append(f"📌 Doğrudan Neden [{imm_code}] {imm_standard}:")
            else:
                report.append(f"📌 Doğrudan Neden [{imm_code}]:")
            report.append(f"   {imm_cause}")
            if imm_evidence:
                report.append(f"   Kanıt: {imm_evidence}")
            report.append("")

            for idx, why in enumerate(whys, 1):
                report.append(f"❓ Neden {idx}? {why.get('question_tr', '')}")
                report.append(f"   → {why.get('answer_tr', '')}")
                report.append("")

            root_code        = root.get('code', '')
            root_standard    = root.get('standard_title_tr', '')
            root_category    = root.get('category_type', '')
            root_cause       = root.get('cause_tr', '')
            root_explanation = root.get('explanation_tr', '')

            if root_standard:
                report.append(f"🎯 KÖK NEDEN [{root_code}] {root_standard} — {root_category}:")
            else:
                report.append(f"🎯 KÖK NEDEN [{root_code}] — {root_category}:")
            report.append(f"   {root_cause}")
            if root_explanation:
                report.append(f"   💡 {root_explanation}")
            report.append("")
            report.append("-" * 80)

        report.append("")
        report.append("📊 ROOT CAUSE ÖZETİ:")
        for i, rc in enumerate(rca_data.get("final_root_causes", []), 1):
            rc_code     = rc.get('code', '')
            rc_standard = rc.get('standard_title_tr', '')
            rc_cause    = rc.get('cause_tr', '')
            if rc_standard:
                report.append(f"  {i}. [{rc_code}] {rc_standard} → {rc_cause}")
            else:
                report.append(f"  {i}. [{rc_code}] {rc_cause}")

        return "\n".join(report)

    # ─────────────────────────────────────────────────────────────────────────
    # YARDIMCI — OLAY ÖZETİ HAZIRLA (V2.2'den aynı)
    # ─────────────────────────────────────────────────────────────────────────

    def _prepare_incident_summary(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None
    ) -> str:
        """Olay özetini hazırla (V2.2 ile aynı)"""

        if investigation_data and isinstance(investigation_data, dict):
            for key in [
                "description",
                "full_description",
                "incident_description",
                "raw_text",
                "how_happened",
            ]:
                val = investigation_data.get(key)
                if val and isinstance(val, str) and len(val.strip()) > 50:
                    print(f"  ✅ Olay özeti kaynağı: investigation_data['{key}'] "
                          f"({len(val)} karakter)")
                    return val.strip()

        if part1_data and isinstance(part1_data, dict):
            for key in [
                "description",
                "incident_description",
                "full_description",
                "raw_text",
            ]:
                val = part1_data.get(key)
                if val and isinstance(val, str) and len(val.strip()) > 50:
                    print(f"  ✅ Olay özeti kaynağı: part1_data['{key}'] "
                          f"({len(val)} karakter)")
                    return val.strip()

        print("  ⚠️  Tam metin bulunamadı, alanlar birleştiriliyor (fallback)")
        summary_parts = []

        if part1_data and isinstance(part1_data, dict):
            brief = part1_data.get("brief_details", {})
            if isinstance(brief, dict):
                if brief.get("what"):
                    summary_parts.append(brief["what"])
                if brief.get("where"):
                    summary_parts.append(f"Konum: {brief['where']}")
                if brief.get("when"):
                    summary_parts.append(f"Zaman: {brief['when']}")
                if brief.get("who"):
                    summary_parts.append(f"İlgili: {brief['who']}")
                if brief.get("how"):
                    summary_parts.append(brief["how"])

            for key in ["incident_type", "type_of_incident", "what_happened"]:
                val = part1_data.get(key)
                if val and isinstance(val, str):
                    summary_parts.append(val)
                    break

        if part2_data and isinstance(part2_data, dict):
            for key in ["type_of_event", "incident_type", "event_description"]:
                val = part2_data.get(key)
                if val and isinstance(val, str):
                    summary_parts.append(f"Olay Tipi: {val}")
                    break

        if investigation_data and isinstance(investigation_data, dict):
            for key in ["how_happened", "narrative", "details"]:
                val = investigation_data.get(key)
                if val and isinstance(val, str):
                    summary_parts.append(val)
                    break

        if summary_parts:
            return ". ".join(summary_parts)

        return "Olay detayı mevcut değil — lütfen investigation_data['description'] alanını doldurun."

    # ─────────────────────────────────────────────────────────────────────────
    # HITL ENTEGRASYON (V2'den aynı)
    # ─────────────────────────────────────────────────────────────────────────

    def _append_hitl_answers(self, summary: str, investigation_data: dict) -> str:
        """HITL 5-why cevaplarını özete ekle (V2'den aynı)"""
        
        if not investigation_data:
            return summary

        answers = investigation_data.get("five_why_answers", [])
        if not answers:
            return summary

        lines = [
            "",
            "",
            "=" * 60,
            "KULLANICI TARAFINDAN TOPLANAN 5-WHY CEVAPLARI (HITL)",
            "=" * 60,
            "ÖNEMLI: Aşağıdaki cevaplar bu olayı soruşturan kişiden",
            "gerçek zamanlı alınmıştır. Kök neden analizini SADECE",
            "bu cevaplara dayandır. Genel varsayım kullanma.",
            "",
        ]

        for fw in answers:
            lvl = fw.get("why_level", "?")
            q   = fw.get("question", "")
            ans = fw.get("user_answer", "")
            d   = fw.get("suggested_direction", "")
            foc = fw.get("hsg245_focus", "")

            lines.append(f"Why-{lvl} Sorusu  : {q}")
            lines.append(f"Why-{lvl} Cevabı  : {ans}")
            if foc:
                lines.append(f"HSG245 Odak     : {foc}")
            if d:
                lines.append(f"Ön Yönlendirme  : {d}")
            lines.append("")

        code  = investigation_data.get("immediate_cause_code", "")
        desc  = investigation_data.get("immediate_cause_desc", "")
        if code:
            lines.append(f"Seçilen Immediate Cause: [{code}] {desc}")
            lines.append("")

        lines.append("=" * 60)
        return summary + "\n".join(lines)
