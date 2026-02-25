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

DEĞİŞİKLİK GEÇMİŞİ:
─────────────────────────────────────────────
V2.0 → V2.1 (Prompt & Diversity Fix):
  - Prompt örnekleri kaldırıldı (model template olarak kullanıyordu)
  - used_root_codes takibi eklendi (dallar arası tekrar engeli)
  - Çeşitlilik ve spesifiklik kuralları eklendi
  - Temperature artırıldı (0.2→0.4 / 0.3→0.6)
  - "Risk değerlendirmesi" tuzağına karşı prompt güçlendirildi

V2.1 → V2.2 (Incident Summary Fix):
  - _prepare_incident_summary tamamen yeniden yazıldı
  - Öncelik sırası: description > full_description > how_happened > alanlar
  - "description" anahtarı artık okunuyor (test dosyası {"description": ...} gönderiyor)
  - Model artık gerçek olay metnini görüyor, kafadan senaryo üretmiyor
─────────────────────────────────────────────
"""

from openai import OpenAI
from typing import Dict, List, Optional
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
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print("✅ Kök Neden Ajanı V2 başlatıldı (knowledge_base)")

    # ─────────────────────────────────────────────────────────────────────────
    # ANA GİRİŞ NOKTASI
    # ─────────────────────────────────────────────────────────────────────────

    def analyze_root_causes(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None
    ) -> Dict:
        """Tam hiyerarşik kök neden analizi"""

        print("\n" + "=" * 80)
        print("🔴 BÖLÜM 3: HİYERARŞİK KÖK NEDEN ANALİZİ")
        print("=" * 80)

        incident_summary = self._prepare_incident_summary(
            part1_data, part2_data, investigation_data
        )
        print(f"\n📋 OLAY ÖZETİ (ilk 300 karakter):\n{incident_summary[:300]}...\n")

        rca_data = {
            "incident_summary": incident_summary,
            "analysis_branches": [],
            "final_root_causes": [],
            "analysis_method": "HSG245 Hierarchical 5-Why (A/B → C/D)"
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
        """A/B kategorilerinden immediate causes bul"""

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
            model="anthropic/claude-sonnet-4.5",
            temperature=0.4,
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
            context="Immediate Causes Identification",
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
    # ADIM 2 — 5-WHY ZİNCİRİ
    # ─────────────────────────────────────────────────────────────────────────

    def _perform_5why_chain(
        self,
        immediate_cause: Dict,
        incident_summary: str,
        used_root_codes: List[str] = None
    ) -> Dict:
        """Bir immediate cause için 5-Why zinciri oluştur"""

        if used_root_codes is None:
            used_root_codes = []

        code     = immediate_cause.get("code", "")
        cause_tr = immediate_cause.get("cause_tr", "")

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
            model="anthropic/claude-opus-4.6",
            temperature=0.6,
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
                                "Jenerik/genel kodlardan kaçın."
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
            context=f"5-Why Chain for {code}",
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
    # YARDIMCI — DAL AĞACI
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
    # YARDIMCI — HİYERARŞİK RAPOR
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_hierarchical_report(self, rca_data: Dict) -> str:
        report = []
        report.append("=" * 80)
        report.append("KÖK NEDEN ANALİZİ RAPORU (HSG245 - 5 Why Metodolojisi)")
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
    # KRİTİK DÜZELTME — OLAY ÖZETİ HAZIRLA
    # ─────────────────────────────────────────────────────────────────────────

    def _prepare_incident_summary(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None
    ) -> str:
        """
        Olay özetini hazırla.

        ÖNCELİK SIRASI (V2.2 düzeltmesi):
        1. investigation_data["description"]        ← test dosyası bunu gönderiyor
        2. investigation_data["full_description"]
        3. investigation_data["incident_description"]
        4. investigation_data["raw_text"]
        5. investigation_data["how_happened"]
        6. part1_data["incident_description"]
        7. part1_data["full_description"]
        8. part1_data["raw_text"]
        9. Fallback: part1_data + part2_data alanlarını birleştir

        SORUN GEÇMİŞİ:
        Eski kod sadece "how_happened" anahtarını arıyordu.
        Test dosyası {"description": INCIDENT_DESCRIPTION} gönderiyor.
        "description" anahtarı hiç okunmadığı için model gerçek olayı
        görmüyor, kafasından senaryo üretiyordu.
        """

        # ── 1. investigation_data içindeki tam metin alanları ──────────────
        if investigation_data and isinstance(investigation_data, dict):
            for key in [
                "description",           # ← test dosyasının gönderdiği anahtar
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

        # ── 2. part1_data içindeki tam metin alanları ──────────────────────
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

        # ── 3. Fallback: alanları birleştir ────────────────────────────────
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

            # Üst seviye alanlar
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