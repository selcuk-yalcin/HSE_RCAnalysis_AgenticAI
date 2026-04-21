"""
Hybrid Session Agent - Uzman-AI Ortak Analiz Sistemi
=====================================================

MİMARİ:
    Rapor → AI Kanıt Çıkarıcı → Uzman Onayı
                                      ↓
                             AI Soru Sorucusu → Uzman Cevapları
                                      ↓
                             AI Yapılandırıcı → HSG245 Kodları + Rapor

AŞAMALAR:
    1. EXTRACT  - AI raporu okur, kritik kanıtları işaretler
    2. CONFIRM  - Uzman kanıtları onaylar / düzeltir / ekler
    3. INTERVIEW - AI her onaylanan kanıt için Why soruları sorar
    4. STRUCTURE - Cevaplar HSG245'e kodlanır, 5-Why zincirleri kurulur
    5. REPORT    - Final rapor üretilir

KULLANIM:
    agent = HybridSessionAgent()
    result = agent.run_session(raw_incident_text)
    # Sistem terminal üzerinden uzmanla diyalog kurar
"""

from openai import OpenAI
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import json

try:
    from .json_parser import safe_json_parse
except ImportError:
    try:
        from json_parser import safe_json_parse
    except ImportError:
        from agents.json_parser import safe_json_parse

try:
    from knowledge_base import get_category_text, get_all_categories
except ImportError:
    try:
        from agents.knowledge_base import get_category_text, get_all_categories
    except ImportError:
        from .knowledge_base import get_category_text, get_all_categories


# ─────────────────────────────────────────────
# RENK VE FORMAT SABİTLERİ (terminal çıktısı)
# ─────────────────────────────────────────────
class Colors:
    AI     = "\033[94m"   # Mavi  → AI konuşuyor
    EXPERT = "\033[92m"   # Yeşil → Uzman girişi bekleniyor
    WARN   = "\033[93m"   # Sarı  → Uyarı
    BOLD   = "\033[1m"
    END    = "\033[0m"


def ai_print(msg: str):
    """AI mesajlarını mavi yazdır"""
    print(f"\n{Colors.AI}{Colors.BOLD}🤖 AI:{Colors.END}{Colors.AI} {msg}{Colors.END}")


def expert_input(prompt: str) -> str:
    """Uzman girişini yeşil prompt ile al"""
    return input(f"\n{Colors.EXPERT}{Colors.BOLD}👤 SİZ: {prompt}{Colors.END}\n→ ").strip()


def section_header(title: str):
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}  {title}{Colors.END}")
    print(f"{'='*70}")


# ─────────────────────────────────────────────
# VERİ YAPILARI
# ─────────────────────────────────────────────

class Evidence:
    """Tek bir kanıt parçası"""
    def __init__(self, text: str, source: str, is_critical: bool = False):
        self.text = text
        self.source = source          # "AI" veya "EXPERT"
        self.is_critical = is_critical
        self.confirmed = False
        self.expert_note = ""

class InterviewAnswer:
    """Uzmanın bir soruya verdiği cevap"""
    def __init__(self, question: str, answer: str, hsg245_code: str = "",
                 hsg245_title: str = "", category: str = ""):
        self.question = question
        self.answer = answer
        self.hsg245_code = hsg245_code
        self.hsg245_title = hsg245_title
        self.category = category

class AnalysisBranch:
    """Bir 5-Why dalı"""
    def __init__(self, perspective: str, immediate_cause_code: str,
                 immediate_cause_text: str, evidence: Evidence):
        self.perspective = perspective
        self.immediate_cause_code = immediate_cause_code
        self.immediate_cause_text = immediate_cause_text
        self.evidence = evidence
        self.why_chain: List[InterviewAnswer] = []
        self.root_cause_code: str = ""
        self.root_cause_title: str = ""
        self.root_cause_explanation: str = ""


# ─────────────────────────────────────────────
# ANA AJAN
# ─────────────────────────────────────────────

class HybridSessionAgent:
    """
    Uzman-AI Ortak Analiz Ajanı
    
    Uzmanın bilgisini sistematik olarak toplayıp
    HSG245 standardına göre yapılandırır.
    """

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "anthropic/claude-3.5-haiku"

        # Oturum verisi
        self.raw_text: str = ""
        self.confirmed_evidences: List[Evidence] = []
        self.branches: List[AnalysisBranch] = []
        self.session_log: List[Dict] = []

        print(f"\n{Colors.BOLD}✅ Hibrit Oturum Ajanı başlatıldı{Colors.END}")

    # ═══════════════════════════════════════════
    # ANA AKIŞ
    # ═══════════════════════════════════════════

    def run_session(self, raw_incident_text: str) -> Dict:
        """
        Tam hibrit oturumu çalıştır.
        Uzmanla terminal üzerinden interaktif diyalog kurar.
        """
        self.raw_text = raw_incident_text

        section_header("HİBRİT KAZA ANALİZİ OTURUMU")
        ai_print(
            "Merhaba. Bu oturumda birlikte çalışacağız.\n"
            "   Ben raporu okuyup kritik noktaları işaretleyeceğim,\n"
            "   siz de bilginizi ekleyeceksiniz.\n"
            "   Sonunda HSG245 standardında bir 5-Why analizi çıkaracağız."
        )

        # ── AŞAMA 1: Kanıt çıkar ──────────────────────────────────────
        section_header("AŞAMA 1/5: KRİTİK KANITLARI TESPİT")
        ai_evidences = self._extract_critical_evidences()

        # ── AŞAMA 2: Uzman onayı ──────────────────────────────────────
        section_header("AŞAMA 2/5: UZMAN ONAYI")
        self.confirmed_evidences = self._expert_confirmation(ai_evidences)

        if not self.confirmed_evidences:
            ai_print("Onaylanmış kanıt yok. Oturum sonlandırılıyor.")
            return {}

        # ── AŞAMA 3: Perspektif seçimi ────────────────────────────────
        section_header("AŞAMA 3/5: ANALİZ PERSPEKTİFLERİ")
        branch_plans = self._plan_branches()

        # ── AŞAMA 4: Her dal için uzman röportajı ────────────────────
        section_header("AŞAMA 4/5: UZMAN RÖPORTAJI (5-WHY)")
        for plan in branch_plans:
            branch = self._conduct_branch_interview(plan)
            self.branches.append(branch)

        # ── AŞAMA 5: Rapor üret ───────────────────────────────────────
        section_header("AŞAMA 5/5: RAPOR OLUŞTURULUYOR")
        final_report = self._generate_final_report()

        # Kaydet
        self._save_session_log(final_report)

        return final_report

    # ═══════════════════════════════════════════
    # AŞAMA 1: KANıT ÇIKARICI
    # ═══════════════════════════════════════════

    def _extract_critical_evidences(self) -> List[Evidence]:
        """
        AI raporu okur ve kritik kanıt adaylarını işaretler.
        Özellikle:
        - Normalization of deviation (gördü ama devam etti)
        - Eksik kontroller (banksman yok, PA yok, izin yok)
        - Karar değişikliği noktaları
        - İletişim kopuklukları
        """
        ai_print("Raporu okuyorum, kritik kanıtları tespit ediyorum...")

        prompt = f"""Sen deneyimli bir İSG soruşturma uzmanısın.
Aşağıdaki olay raporunu oku ve en kritik 5-7 kanıtı tespit et.

ÖZELLİKLE ŞUNLARA BAK:
1. "Gördü ama devam etti" türü sapma normalleşmesi
2. Eksik kontroller (banksman, gözetmen, izin, tarama)
3. Karar değişikliği noktaları ve gerekçeleri
4. İletişim kopuklukları veya bilgi eksiklikleri
5. Önceki deneyimin yanlış güven yarattığı anlar
6. Liderlik/otoritenin kullanılmadığı kritik anlar

RAPOR:
{self.raw_text[:4000]}

Her kanıt için:
- text: Rapordan doğrudan alıntı veya özet (1-2 cümle)
- why_critical: Neden kritik olduğunu açıkla (investigator gözüyle)
- suggested_perspective: Bu kanıtın hangi analiz boyutuna işaret ettiği
  (OPERATÖR_HATASI / TEKNİK_DURUM / GÖZETİM_BAŞARISIZLIĞI / 
   KARAR_ALMA / KÜLTÜR_VE_LİDERLİK / SİSTEM_TASARIM)

JSON:
{{
  "evidences": [
    {{
      "id": 1,
      "text": "Kablo kesilmesine rağmen ekip kazıya devam etti",
      "why_critical": "Aktif tehlike tespit edilmesine rağmen iş durdurulmadı - normalization of deviation",
      "suggested_perspective": "KÜLTÜR_VE_LİDERLİK"
    }}
  ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Kanıt çıkarıcı. Sadece JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        data = safe_json_parse(
            response.choices[0].message.content,
            context="Evidence Extraction",
            default={"evidences": []}
        )

        evidences = []
        raw_list = data.get("evidences", [])

        print(f"\n   {len(raw_list)} kritik kanıt adayı tespit edildi:\n")
        for i, e in enumerate(raw_list, 1):
            print(f"   [{i}] {e.get('text','')[:80]}")
            print(f"        → {e.get('why_critical','')[:70]}")
            print(f"        📌 Perspektif: {e.get('suggested_perspective','')}\n")
            evidences.append(Evidence(
                text=e.get("text", ""),
                source="AI",
                is_critical=True
            ))
            # Meta bilgiyi sakla
            evidences[-1].why_critical = e.get("why_critical", "")
            evidences[-1].suggested_perspective = e.get("suggested_perspective", "")
            evidences[-1].id = i

        return evidences

    # ═══════════════════════════════════════════
    # AŞAMA 2: UZMAN ONAY DÖNGÜSÜ
    # ═══════════════════════════════════════════

    def _expert_confirmation(self, ai_evidences: List[Evidence]) -> List[Evidence]:
        """
        Uzman her kanıtı onaylar, düzeltir veya ekler.
        """
        ai_print(
            f"Tespit ettiğim {len(ai_evidences)} kanıtı tek tek onaylamanızı isteyeceğim.\n"
            "   Her biri için: [ENTER]=Onayla  |  [d]=Düzelt  |  [s]=Sil\n"
            "   Sonunda ek kanıt da ekleyebilirsiniz."
        )

        confirmed = []

        for ev in ai_evidences:
            print(f"\n{'─'*60}")
            print(f"  {Colors.BOLD}Kanıt [{ev.id}]:{Colors.END}")
            print(f"  {ev.text}")
            print(f"  {Colors.WARN}Neden kritik:{Colors.END} {ev.why_critical}")
            print(f"  {Colors.WARN}Perspektif:{Colors.END} {ev.suggested_perspective}")

            choice = expert_input("[ENTER]=Onayla | [d]=Düzelt | [s]=Sil").lower()

            if choice == "s":
                print(f"   ✗ Kanıt silindi")
                continue
            elif choice == "d":
                new_text = expert_input("Düzeltilmiş kanıtı yazın")
                if new_text:
                    ev.text = new_text
                    ev.expert_note = "Uzman tarafından düzeltildi"
                    ev.source = "EXPERT"
                print(f"   ✓ Kanıt güncellendi")
            else:
                print(f"   ✓ Onaylandı")

            ev.confirmed = True
            confirmed.append(ev)

            self.session_log.append({
                "phase": "confirmation",
                "evidence_id": ev.id,
                "action": choice or "confirm",
                "final_text": ev.text
            })

        # Uzman ek kanıt ekleyebilir
        print(f"\n{'─'*60}")
        ai_print("Sizin eklemek istediğiniz kritik bir kanıt var mı?")
        while True:
            add = expert_input("[ENTER]=Hayır  |  Kanıtı yazın").strip()
            if not add:
                break
            perspective = expert_input(
                "Bu kanıt hangi perspektifi işaret ediyor?\n"
                "  1=Operatör hatası  2=Teknik durum  3=Gözetim  "
                "4=Karar alma  5=Kültür/Liderlik  6=Sistem"
            )
            perspective_map = {
                "1": "OPERATÖR_HATASI", "2": "TEKNİK_DURUM",
                "3": "GÖZETİM_BAŞARISIZLIĞI", "4": "KARAR_ALMA",
                "5": "KÜLTÜR_VE_LİDERLİK", "6": "SİSTEM_TASARIM"
            }
            new_ev = Evidence(text=add, source="EXPERT", is_critical=True)
            new_ev.suggested_perspective = perspective_map.get(perspective, "GENEL")
            new_ev.why_critical = "Uzman tarafından eklendi"
            new_ev.id = len(confirmed) + 1
            new_ev.confirmed = True
            confirmed.append(new_ev)
            print(f"   ✓ Kanıt eklendi")

        ai_print(f"{len(confirmed)} kanıt onaylandı. Analiz başlıyor.")
        return confirmed

    # ═══════════════════════════════════════════
    # AŞAMA 3: BRANCH PLANLAMA
    # ═══════════════════════════════════════════

    def _plan_branches(self) -> List[Dict]:
        """
        Onaylanan kanıtlara dayanarak kaç dal açılacağını
        ve her dalın perspektifini AI önerir, uzman onaylar.
        """
        # Kanıtları perspektife göre grupla
        perspective_groups = {}
        for ev in self.confirmed_evidences:
            p = getattr(ev, "suggested_perspective", "GENEL")
            if p not in perspective_groups:
                perspective_groups[p] = []
            perspective_groups[p].append(ev)

        ai_print(
            f"Onaylanan kanıtlara dayanarak şu analiz dallarını öneriyorum:\n"
        )

        # AI dal önerileri oluştur
        prompt = f"""Olay analizi için dal planı oluştur.

ONAYLANAN KANITLAR:
{json.dumps([{"id": e.id, "text": e.text, "perspective": getattr(e, "suggested_perspective", "")} 
             for e in self.confirmed_evidences], ensure_ascii=False, indent=2)}

HSG245 A KATEGORİSİ (Davranışsal):
{get_category_text('A')[:800]}

HSG245 B KATEGORİSİ (Koşullar):
{get_category_text('B')[:800]}

3 analiz dalı öner. Her dal:
- Farklı bir perspektiften bakmalı (operatör / teknik / gözetim)
- Kanıtlardan en az biriyle desteklenmeli
- Farklı bir kök nedene ulaşabilmeli

JSON:
{{
  "branches": [
    {{
      "branch_number": 1,
      "perspective": "OPERATÖR HATASI - Dikkat ve Karar Verme",
      "immediate_cause_code": "A4.5",
      "immediate_cause_title": "Kasıtsız insan hatası",
      "immediate_cause_text": "Olaya özgü açıklama",
      "supporting_evidence_ids": [1, 3],
      "target_root_cause_hint": "C kategorisi - kişisel faktör"
    }}
  ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Dal planlayıcı. Sadece JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        data = safe_json_parse(
            response.choices[0].message.content,
            context="Branch Planning",
            default={"branches": []}
        )

        branch_plans = data.get("branches", [])

        # Uzmana göster ve onaylat
        for bp in branch_plans:
            print(f"\n  {Colors.BOLD}Dal {bp.get('branch_number')}:{Colors.END} "
                  f"{bp.get('perspective','')}")
            print(f"  Doğrudan Neden [{bp.get('immediate_cause_code','')}]: "
                  f"{bp.get('immediate_cause_text','')[:70]}")
            print(f"  Destekleyen kanıtlar: {bp.get('supporting_evidence_ids','')}")

        print()
        ai_print("Bu dal yapısını onaylıyor musunuz?")
        choice = expert_input("[ENTER]=Onayla | [d]=Değiştir").lower()

        if choice == "d":
            change = expert_input(
                "Hangi dalı değiştirmek istiyorsunuz? Açıklayın\n"
                "(Örn: 'Dal 2 gözetim yerine yüklenici yönetimini ele almalı')"
            )
            # Değişikliği log'a kaydet, basit güncelleme
            self.session_log.append({
                "phase": "branch_planning",
                "expert_change": change
            })
            ai_print(f"Not alındı: {change}\nDevam ediyorum.")

        return branch_plans

    # ═══════════════════════════════════════════
    # AŞAMA 4: DAL RÖPORTAJI
    # ═══════════════════════════════════════════

    def _conduct_branch_interview(self, plan: Dict) -> AnalysisBranch:
        """
        Bir dal için uzmanla 4-5 soru sorarak Why zinciri kur.
        Her cevabı otomatik HSG245 koduna çevir.
        """
        bn = plan.get("branch_number", "?")
        perspective = plan.get("perspective", "")
        imm_code = plan.get("immediate_cause_code", "")
        imm_text = plan.get("immediate_cause_text", "")

        # Destekleyen kanıtları bul
        evidence_ids = plan.get("supporting_evidence_ids", [])
        supporting = [e for e in self.confirmed_evidences
                      if getattr(e, "id", -1) in evidence_ids]
        main_evidence = supporting[0] if supporting else Evidence(
            text=imm_text, source="AI"
        )

        branch = AnalysisBranch(
            perspective=perspective,
            immediate_cause_code=imm_code,
            immediate_cause_text=imm_text,
            evidence=main_evidence
        )

        print(f"\n{'─'*70}")
        ai_print(
            f"DAL {bn}: {perspective}\n"
            f"   Doğrudan Neden [{imm_code}]: {imm_text}\n\n"
            f"   Şimdi bu nedeni birlikte derinleştireceğiz.\n"
            f"   4 soru soracağım, her cevabınız bir Why basamağı olacak."
        )

        # AI her Why sorusunu dinamik olarak üretir
        # (önceki cevaplara dayanarak)
        conversation_context = [
            f"Olay: {self.raw_text[:1000]}",
            f"Dal perspektifi: {perspective}",
            f"Doğrudan neden: [{imm_code}] {imm_text}"
        ]

        for why_level in range(1, 5):
            question = self._generate_why_question(
                why_level, conversation_context, plan
            )

            ai_print(f"Neden {why_level}: {question}")
            answer = expert_input("Cevabınız")

            if not answer:
                answer = "[Uzman cevaplamadı]"

            # Cevabı HSG245'e kodla
            coded = self._code_answer_to_hsg245(
                question, answer, why_level,
                perspective, conversation_context
            )

            interview_answer = InterviewAnswer(
                question=question,
                answer=answer,
                hsg245_code=coded.get("code", ""),
                hsg245_title=coded.get("title", ""),
                category=coded.get("category", "")
            )

            branch.why_chain.append(interview_answer)
            conversation_context.append(f"Neden {why_level}: {question} → {answer}")

            # Kodlamayı uzmanla paylaş
            if coded.get("code"):
                print(f"   {Colors.WARN}[{coded['code']}] "
                      f"{coded['title']}{Colors.END}")

        # Kök neden tespiti
        root = self._identify_root_cause(branch, conversation_context)
        branch.root_cause_code = root.get("code", "")
        branch.root_cause_title = root.get("title", "")
        branch.root_cause_explanation = root.get("explanation", "")

        print(f"\n   {Colors.BOLD}🎯 KÖK NEDEN [{branch.root_cause_code}]: "
              f"{branch.root_cause_title}{Colors.END}")
        print(f"   {branch.root_cause_explanation[:120]}")

        # Uzman onayı
        confirm = expert_input(
            f"Bu kök neden doğru mu? [ENTER]=Evet | Hayırsa doğrusunu yazın"
        )
        if confirm:
            branch.root_cause_explanation = confirm
            self.session_log.append({
                "phase": "root_cause_correction",
                "branch": bn,
                "expert_correction": confirm
            })

        return branch

    def _generate_why_question(self, level: int, context: List[str],
                                plan: Dict) -> str:
        """
        Önceki cevaplara dayanarak bir sonraki Why sorusunu üret.
        Her soru öncekinden farklı bir boyutu açmalı.
        """
        level_guidance = {
            1: "Operasyonel — tam olarak ne oldu / ne yapıldı / yapılmadı?",
            2: "Taktik — neden o şekilde yapıldı / yapılmadı?",
            3: "Sistem — hangi prosedür veya kontrol bu duruma izin verdi?",
            4: "Organizasyonel — bu sistem neden böyle tasarlandı / uygulandı?"
        }

        prompt = f"""Bir İSG 5-Why analizi yapılıyor.

BAĞLAM:
{chr(10).join(context[-5:])}

DAL PERSPEKTİFİ: {plan.get('perspective','')}
HEDEF KÖK NEDEN: {plan.get('target_root_cause_hint','')}

Şimdi Neden {level} sorusunu üret.
Yönlendirme: {level_guidance.get(level,'')}

KURAL: Soru, önceki cevaplardan FARKLI bir boyutu sormalı.
Kısa ve net olsun (1 cümle).

Sadece soruyu döndür, başka bir şey yazma."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    def _code_answer_to_hsg245(self, question: str, answer: str,
                                level: int, perspective: str,
                                context: List[str]) -> Dict:
        """
        Uzmanın cevabını HSG245 kategorisine kodla.
        Level 1-3 için A/B kategorisi, level 4+ için C/D kategorisi.
        """
        if level <= 2:
            taxonomy = get_category_text('A') + "\n" + get_category_text('B')
            categories = "A (Davranışsal) veya B (Koşullar)"
        else:
            taxonomy = get_category_text('C') + "\n" + get_category_text('D')
            categories = "C (Kişisel) veya D (Organizasyonel)"

        prompt = f"""Bu cevabı HSG245 kategorisine kodla.

Soru: {question}
Cevap: {answer}
Seviye: {level} ({"erken" if level <= 2 else "derin"} neden)
Perspektif: {perspective}

Uygun kategori: {categories}

REFERANS:
{taxonomy[:1500]}

JSON:
{{"code": "D1.2", "title": "Yetersiz gözetim veya denetim", 
  "category": "ORGANİZASYONEL", "confidence": 0.85}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            max_tokens=150,
            messages=[
                {"role": "system", "content": "HSG245 kodlayıcı. Sadece JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        return safe_json_parse(
            response.choices[0].message.content,
            context="HSG245 Coding",
            default={"code": "", "title": "", "category": "", "confidence": 0}
        )

    def _identify_root_cause(self, branch: AnalysisBranch,
                              context: List[str]) -> Dict:
        """
        Why zincirinin tamamından kök nedeni sentezle.
        """
        why_summary = "\n".join([
            f"N{i+1}: {wa.question} → {wa.answer} [{wa.hsg245_code}]"
            for i, wa in enumerate(branch.why_chain)
        ])

        prompt = f"""Why zincirinden kök nedeni sentezle.

PERSPEKTİF: {branch.perspective}

WHY ZİNCİRİ:
{why_summary}

D KATEGORİSİ:
{get_category_text('D')[:1500]}
C KATEGORİSİ:
{get_category_text('C')[:800]}

Bu dala özgü en uygun kök nedeni seç.
Diğer dallardan FARKLI bir kod tercih et.

JSON:
{{"code": "D1.5", "title": "Sapmaların normalleşmesi", 
  "category": "ORGANİZASYONEL",
  "explanation": "Bu dalın kök nedenini 2-3 cümleyle açıkla"}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Kök neden sentezleyici. Sadece JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        return safe_json_parse(
            response.choices[0].message.content,
            context="Root Cause Identification",
            default={"code": "D4.1", "title": "Risk analizi yetersiz",
                     "category": "ORGANİZASYONEL", "explanation": ""}
        )

    # ═══════════════════════════════════════════
    # AŞAMA 5: RAPOR ÜRETIMI
    # ═══════════════════════════════════════════

    def _generate_final_report(self) -> Dict:
        """
        Tüm oturum verilerinden final HSG245 raporu üret.
        """
        ai_print("Tüm cevaplarınızı HSG245 formatında düzenliyorum...")

        report = {
            "generated_at": datetime.now().isoformat(),
            "method": "Hibrit Uzman-AI Analizi",
            "evidences_confirmed": len(self.confirmed_evidences),
            "branches": [],
            "root_causes_summary": [],
            "narrative": "",
            "recommendations": []
        }

        # Dalları yapılandır
        for branch in self.branches:
            branch_data = {
                "perspective": branch.perspective,
                "immediate_cause": {
                    "code": branch.immediate_cause_code,
                    "text": branch.immediate_cause_text,
                    "evidence": branch.evidence.text
                },
                "why_chain": [
                    {
                        "level": i + 1,
                        "question": wa.question,
                        "answer": wa.answer,
                        "hsg245_code": wa.hsg245_code,
                        "hsg245_title": wa.hsg245_title
                    }
                    for i, wa in enumerate(branch.why_chain)
                ],
                "root_cause": {
                    "code": branch.root_cause_code,
                    "title": branch.root_cause_title,
                    "explanation": branch.root_cause_explanation
                }
            }
            report["branches"].append(branch_data)
            report["root_causes_summary"].append({
                "code": branch.root_cause_code,
                "title": branch.root_cause_title,
                "perspective": branch.perspective
            })

        # Kök neden çeşitliliği kontrolü
        codes = [rc["code"] for rc in report["root_causes_summary"]]
        unique_codes = set(codes)
        if len(unique_codes) < len(codes):
            ai_print(
                f"⚠️  Uyarı: Bazı kök nedenler tekrar ediyor: {codes}\n"
                "   Uzman incelemesi önerilir."
            )

        # Öneriler üret
        report["recommendations"] = self._generate_recommendations(report)

        # Terminal çıktısı
        self._print_final_report(report)

        return report

    def _generate_recommendations(self, report: Dict) -> List[Dict]:
        """Her kök nedenden SMART aksiyon üret"""
        root_causes_text = "\n".join([
            f"[{rc['code']}] {rc['title']} ({rc['perspective']})"
            for rc in report["root_causes_summary"]
        ])

        prompt = f"""Bu kök nedenler için SMART aksiyonlar üret.

KÖK NEDENLER:
{root_causes_text}

Her kök neden için 1 aksiyon:
- Spesifik ve ölçülebilir
- Sorumlu pozisyon belirt
- Kapanış kriteri belirt

JSON:
{{
  "recommendations": [
    {{
      "root_cause_code": "D1.2",
      "action": "Spesifik aksiyon",
      "responsible": "Pozisyon/Rol",
      "completion_criteria": "Ne zaman kapalı sayılır",
      "priority": "HIGH/MEDIUM/LOW"
    }}
  ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "SMART aksiyon üretici. Sadece JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        data = safe_json_parse(
            response.choices[0].message.content,
            context="Recommendations",
            default={"recommendations": []}
        )
        return data.get("recommendations", [])

    def _print_final_report(self, report: Dict):
        """Terminal'e okunabilir final rapor yazdır"""
        section_header("FINAL RAPOR — HSG245 5-WHY ANALİZİ")
        print(f"  Yöntem  : {report['method']}")
        print(f"  Tarih   : {report['generated_at'][:10]}")
        print(f"  Kanıt   : {report['evidences_confirmed']} onaylanmış kanıt")

        for i, branch in enumerate(report["branches"], 1):
            print(f"\n{'─'*60}")
            print(f"  {Colors.BOLD}DAL {i}: {branch['perspective']}{Colors.END}")
            print(f"  📌 [{branch['immediate_cause']['code']}] "
                  f"{branch['immediate_cause']['text']}")
            print(f"  Kanıt: {branch['immediate_cause']['evidence'][:60]}")
            print()
            for why in branch["why_chain"]:
                print(f"  ❓ N{why['level']}: {why['question']}")
                print(f"     → {why['answer']}")
                if why.get("hsg245_code"):
                    print(f"     [{why['hsg245_code']}] {why['hsg245_title']}")
            print(f"\n  {Colors.BOLD}🎯 KÖK NEDEN [{branch['root_cause']['code']}]: "
                  f"{branch['root_cause']['title']}{Colors.END}")
            print(f"  {branch['root_cause']['explanation'][:120]}")

        print(f"\n{'─'*60}")
        print(f"  {Colors.BOLD}📊 KÖK NEDEN ÖZETİ:{Colors.END}")
        for rc in report["root_causes_summary"]:
            print(f"  [{rc['code']}] {rc['title']}")

        if report.get("recommendations"):
            print(f"\n  {Colors.BOLD}✅ ÖNERİLER:{Colors.END}")
            for r in report["recommendations"]:
                print(f"  [{r.get('root_cause_code','')}] {r.get('action','')[:70]}")
                print(f"       Sorumlu: {r.get('responsible','')} | "
                      f"Öncelik: {r.get('priority','')}")

    def _save_session_log(self, report: Dict):
        """Oturum logunu kaydet"""
        log_data = {
            "session_log": self.session_log,
            "final_report": report
        }
        filepath = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        ai_print(f"Oturum kaydedildi: {filepath}")


# ─────────────────────────────────────────────
# KULLANIM ÖRNEĞİ
# ─────────────────────────────────────────────

def run_hybrid_analysis(incident_text: str) -> Dict:
    """
    Tek satırda hibrit analiz başlat.
    
    Örnek:
        from hybrid_session_agent import run_hybrid_analysis
        result = run_hybrid_analysis(incident_report_text)
    """
    agent = HybridSessionAgent()
    return agent.run_session(incident_text)


if __name__ == "__main__":
    # Test modu — örnek olay metniyle çalıştır
    sample = """
    On July 30, 2024, during a mechanical excavation with a backhoe loader (JCB), 
    the contractor's excavation team damaged under-construction cathodic protection cables.
    One cable was severed. The team continued excavation after the first cable was cut.
    Line detection was performed but could not detect inactive cables.
    The PA and Site Engineer were newly appointed to this location.
    """
    result = run_hybrid_analysis(sample)
