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

DEĞİŞİKLİKLER (V2 → V2.1):
- Prompt örnekleri kaldırıldı (model template olarak kullanıyordu)
- used_root_codes takibi eklendi (dallar arası tekrar engeli)
- Çeşitlilik ve spesifiklik kuralları eklendi
- Temperature artırıldı (0.2→0.4 / 0.3→0.6)
- "Risk değerlendirmesi" tuzağına karşı prompt güçlendirildi
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

        # Olay özeti hazırla
        incident_summary = self._prepare_incident_summary(
            part1_data, part2_data, investigation_data
        )
        print(f"\n📋 OLAY ÖZETİ:\n{incident_summary}\n")

        # Ana yapı
        rca_data = {
            "incident_summary": incident_summary,
            "analysis_branches": [],   # Her dal bir immediate cause + 5-why chain
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

        # ── Dallar arası tekrar engelleyici liste ──────────────────────────
        used_root_codes: List[str] = []

        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n{'=' * 80}")
            print(f"⚡ DAL {idx}: {immediate_cause.get('category_type', '???')}")
            print(f"📌 Doğrudan Neden [{immediate_cause.get('code', '???')}]:")
            print(f"   {immediate_cause.get('cause_tr', immediate_cause.get('cause', ''))}")
            print(f"{'=' * 80}\n")

            # 5-Why chain oluştur — kullanılan kodları ilet
            chain = self._perform_5why_chain(
                immediate_cause,
                incident_summary,
                used_root_codes=used_root_codes
            )

            # Kullanılan root cause kodunu listeye ekle (bir sonraki dal görecek)
            root_code = chain.get("root_cause", {}).get("code")
            if root_code:
                used_root_codes.append(root_code)

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

        print("\n" + "=" * 80)
        print("✅ TÜM DALLAR TAMAMLANDI!")
        print("=" * 80)

        # Özet rapor oluştur
        rca_data["final_report_tr"] = self._generate_hierarchical_report(rca_data)
        return rca_data

    # ─────────────────────────────────────────────────────────────────────────
    # ADIM 1 — DOĞRUDAN NEDENLER (A / B KATEGORİLERİ)
    # ─────────────────────────────────────────────────────────────────────────

    def _identify_immediate_causes_with_codes(self, incident_summary: str) -> List[Dict]:
        """
        A/B kategorilerinden immediate causes bul.

        DEĞİŞİKLİKLER:
        - Prompt içindeki A1.4 JSON örneği kaldırıldı
        - Çeşitlilik (A+B dengesi) kuralı eklendi
        - "Genel nedenler doğrudan neden olamaz" kuralı eklendi
        - Temperature 0.2 → 0.4
        """
        rag_context_a = get_category_text('A')
        rag_context_b = get_category_text('B')

        prompt = f"""Sen uzman bir İSG Müfettişisin. Görevin, aşağıdaki iş kazası raporunu analiz etmek
ve HSG245 standardına göre "Doğrudan Nedenleri" (Immediate Causes) belirlemektir.

GİRDİLER:

OLAY ÖZETİ:
{incident_summary}

REFERANS LİSTESİ A (DAVRANIŞSAL KODLAR):
{rag_context_a}

REFERANS LİSTESİ B (KOŞULLAR KODLARI):
{rag_context_b}

─────────────────────────────────────────────
KRİTİK KURALLAR:
─────────────────────────────────────────────

1. FİLTRELEME
   Sadece kazayı DOĞRUDAN tetikleyen, olayın hemen öncesinde gerçekleşen nedenleri seç.
   Dolaylı veya arka plan faktörlerini (eğitim eksikliği, risk değerlendirmesi vb.) SEÇME —
   bunlar root cause kategorisine aittir.

2. LİMİT
   Maksimum 3 (ÜÇ) adet en kritik neden. Daha az da olabilir, zorla doldurma.

3. ÇEŞİTLİLİK
   Mümkünse hem A (davranış) hem B (koşul) kategorisinden neden seç.
   Tüm nedenleri tek kategoriye yığma.

4. SPESİFİKLİK
   "Risk değerlendirmesi eksik", "eğitim yetersiz" gibi genel ifadeler DOĞRUDAN NEDEN DEĞİLDİR.
   Bu olaydaki SOMUT, GÖZLEMLENEBILIR eylemi veya koşulu kodla.
   Örnek yaklaşım: "Operatör makineyi durdurmadan müdahale etti" → A kategorisi
                   "Koruyucu kapak mevcut değildi" → B kategorisi

5. SIRALAMA
   En kritikten aza doğru sırala.

6. FORMAT
   Sadece saf JSON çıktısı ver. Markdown etiketi (```json) KULLANMA.

─────────────────────────────────────────────
ALAN TANIMLARI:
─────────────────────────────────────────────
- "code"             : Referans listesinden seçtiğin kod (örn: A2.1)
- "standard_title_tr": O kodun referans listesindeki STANDART BAŞLIĞI (birebir al, değiştirme)
- "category_type"    : "DAVRANIŞSAL" veya "KOŞUL"
- "cause_tr"         : Bu olaya özgü somut açıklama (genel kalıplardan kaçın)
- "evidence_tr"      : Olay özetinden bu kararı destekleyen SOMUT KANIT veya ALINTI

─────────────────────────────────────────────
BEKLENEN ÇIKTI (JSON ŞEMASI — içerik değil, sadece format):
─────────────────────────────────────────────
{{
  "causes": [
    {{
      "code": "<A veya B kategorisinden uygun kod>",
      "standard_title_tr": "<referans listesindeki orijinal Türkçe başlık>",
      "category_type": "<DAVRANIŞSAL veya KOŞUL>",
      "cause_tr": "<bu olaya özgü somut açıklama>",
      "evidence_tr": "<olay özetinden alınan somut kanıt>"
    }}
  ]
}}
"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            temperature=0.4,   # 0.2 → 0.4 (daha esnek kod seçimi)
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Sen HSG245 uzmanısın. "
                                "Sadece JSON döndür, Türkçe içerik kullan. "
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
    # ADIM 2 — 5-WHY ZİNCİRİ (C / D KATEGORİLERİNE UZANAN)
    # ─────────────────────────────────────────────────────────────────────────

    def _perform_5why_chain(
        self,
        immediate_cause: Dict,
        incident_summary: str,
        used_root_codes: List[str] = None
    ) -> Dict:
        """
        Bir immediate cause için 5-Why zinciri oluştur.
        Son Why → C/D kategorisinden root cause.

        DEĞİŞİKLİKLER:
        - used_root_codes parametresi eklendi (dallar arası tekrar engeli)
        - Prompt içindeki D6.1 JSON örneği kaldırıldı
        - "Risk değerlendirmesi" tuzağına karşı uyarı eklendi
        - Temperature 0.3 → 0.6
        """
        if used_root_codes is None:
            used_root_codes = []

        code     = immediate_cause.get("code", "")
        cause_tr = immediate_cause.get("cause_tr", "")

        rag_context_c = get_category_text('C')
        rag_context_d = get_category_text('D')

        # Yasaklı kodları okunabilir formatta hazırla
        if used_root_codes:
            banned_codes_str = (
                "YASAK KODLAR (önceki dallarda zaten seçildi, bunları ROOT CAUSE olarak SEÇME):\n"
                + ", ".join(used_root_codes)
                + "\nFarklı, daha spesifik bir kod bul."
            )
        else:
            banned_codes_str = "Henüz kullanılmış kod yok."

        prompt = f"""Sen İSG kök neden uzmanısın. 5-Why analizi yapıyorsun.

OLAY:
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

1. Bu doğrudan neden için mantıksal bir 5-Why zinciri kur.
   - Why 1 ve Why 2 → Doğrudan nedeni tetikleyen ara faktörler
   - Why 3 ve Why 4 → Daha derin sistemik faktörler
   - Why 5 → Root Cause (C veya D kategorisinden KOD ile)

2. Zincir LİNEER olmalı: her "neden?" bir önceki cevabı sorgular.
   Olay özetindeki gerçek bulgulara dayan, spekülatif olma.

3. Root cause için HSG245 tablosundaki standart Türkçe başlığı "standard_title_tr" alanına ekle.

─────────────────────────────────────────────
KRİTİK KURALLAR:
─────────────────────────────────────────────

A) {banned_codes_str}

B) SPESİFİKLİK KURALI
   "Risk değerlendirmesi eksikliği" (D1.x), "eğitim eksikliği" (D2.x) gibi kodlar
   HER KAZAYA uygulanabilecek jenerik kodlardır.
   Bu olay için DAHA SPESİFİK bir root cause varsa onu seç.
   Genel kodları ancak başka uygun kod yoksa kullan.

C) BAĞLAM KURALI
   Root cause, 5-Why zincirinin mantıksal sonucu olmalı.
   Zincirsiz, "havadan" bir root cause atama.

─────────────────────────────────────────────
DÖNDÜR (JSON ŞEMASI — içerik değil, sadece format):
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
            model="anthropic/claude-3.5-haiku",
            temperature=0.6,   # 0.3 → 0.6 (çeşitlilik için artırıldı)
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Sen 5-Why uzmanısın. Sadece JSON, Türkçe içerik. "
                                "Her kaza için özgün, spesifik kök nedenler üret. "
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

        # Why'ları yazdır
        for why in chain.get("whys", []):
            level    = why.get("level", "?")
            question = why.get("question_tr", "")
            answer   = why.get("answer_tr", "")
            print(f"  ❓ Neden {level}? {question}")
            print(f"     → {answer}\n")

        # Root cause yazdır
        root           = chain.get("root_cause", {})
        root_code      = root.get('code', '???')
        root_standard  = root.get('standard_title_tr', '')
        root_cause_desc = root.get('cause_tr', '')
        root_explanation = root.get('explanation_tr', '')

        if root_standard:
            print(f"  🎯 KÖK NEDEN [{root_code}] {root_standard}: {root_cause_desc}")
        else:
            print(f"  🎯 KÖK NEDEN [{root_code}]: {root_cause_desc}")
        print(f"     ({root_explanation})\n")

        return chain

    # ─────────────────────────────────────────────────────────────────────────
    # YARDIMCI — DAL AĞACI YAZICI
    # ─────────────────────────────────────────────────────────────────────────

    def _print_branch_tree(self, branch: Dict):
        """Dal ağacını güzel yazdır"""
        immediate = branch["immediate_cause"]
        whys      = branch["why_chain"]
        root      = branch["root_cause"]

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
            whys      = branch["why_chain"]
            root      = branch["root_cause"]

            report.append("")
            report.append(f"⚡ DAL {branch['branch_number']}: {immediate.get('category_type', '')}")
            report.append("")

            imm_code      = immediate.get('code', '')
            imm_standard  = immediate.get('standard_title_tr', '')
            imm_cause     = immediate.get('cause_tr', '')
            imm_evidence  = immediate.get('evidence_tr', '')

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

        # Genel özet
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
    # YARDIMCI — OLAY ÖZETİ HAZIRLA
    # ─────────────────────────────────────────────────────────────────────────

    def _prepare_incident_summary(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None
    ) -> str:
        """Olay özetini hazırla"""
        summary_parts = []

        brief = part1_data.get("brief_details", {})
        if isinstance(brief, dict):
            if brief.get("what"):
                summary_parts.append(f"{brief['what']}")
            if brief.get("where"):
                summary_parts.append(f"Konum: {brief['where']}")

        if part2_data.get("type_of_event"):
            summary_parts.append(f"Olay Tipi: {part2_data['type_of_event']}")

        if investigation_data and investigation_data.get("how_happened"):
            summary_parts.append(investigation_data["how_happened"])

        return (
            ". ".join(summary_parts)
            if summary_parts
            else "Olay detayı mevcut değil"
        )
