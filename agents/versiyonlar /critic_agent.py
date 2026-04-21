"""
Critic Agent - Kök Neden Analizi Kalite Kontrol Ajanı
======================================================

GÖREV:
RootCauseAgentV2'nin ürettiği her dal ve kök nedeni bağımsız olarak
eleştirir, puanlar ve gerektiğinde yeniden üretilmesini talep eder.

MİMARİ:
    RootCauseAgentV2 (Üretici)
            ↓
        CriticAgent (Eleştirmen)
            ↓ [PASS/REVISE/REJECT]
    RootCauseAgentV2 (Yeniden üretici - gerekirse)
            ↓
        Final Output

ELEŞTİRİ KRİTERLERİ:
1. ÇEŞİTLİLİK  - Kök nedenler birbirinden gerçekten farklı mı?
2. DERİNLİK    - 5-Why zinciri gerçekten derinleşiyor mu, döngüye mi giriyor?
3. BOYUTLULUK  - İnsan, teknik, organizasyonel boyutlar var mı?
4. KANIT       - Her neden rapordaki somut kanıta dayanıyor mu?
5. MANTIK      - Why zinciri mantıksal olarak birbirine bağlı mı?
6. KAPSAM      - ROO raporundaki kritik faktörler (banksman, PA yokluğu vb.) yansıtıldı mı?
"""

from openai import OpenAI
from typing import Dict, List, Tuple, Optional
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
    from knowledge_base import get_category_text
except ImportError:
    try:
        from agents.knowledge_base import get_category_text
    except ImportError:
        from .knowledge_base import get_category_text


# ============================================================
# KARAR EŞİKLERİ
# ============================================================
PASS_THRESHOLD = 7.0       # >= 7.0 → PASS (kabul)
REVISE_THRESHOLD = 5.0     # 5.0-6.9 → REVISE (düzelt)
REJECT_THRESHOLD = 5.0     # < 5.0 → REJECT (tamamen yeniden üret)
MAX_REVISION_ATTEMPTS = 2  # Maksimum revizyon denemesi


class CriticAgent:
    """
    Eleştirmen Ajan - Üretici ajanın çıktısını denetler.
    
    Üç karar verebilir:
    - PASS   : Analiz yeterli kalitede, devam et
    - REVISE : Belirli sorunlar var, hedefli düzeltme iste
    - REJECT : Analiz köklü biçimde hatalı, sıfırdan yeniden üret
    """
    
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.critique_history: List[Dict] = []
        print("✅ Eleştirmen Ajan başlatıldı")
    
    # ============================================================
    # ANA GİRİŞ NOKTASI
    # ============================================================
    
    def review_full_analysis(self, rca_data: Dict, incident_summary: str) -> Dict:
        """
        Tüm RCA çıktısını gözden geçir.
        Hem bütünsel hem de dal bazında eleştiri yapar.
        
        Returns:
            {
                "overall_verdict": "PASS" | "REVISE" | "REJECT",
                "overall_score": float,
                "branch_reviews": [...],
                "global_issues": [...],
                "revision_instructions": {...},
                "approved_branches": [...],
                "branches_to_revise": [...],
                "branches_to_reject": [...]
            }
        """
        print("\n" + "="*80)
        print("🔍 ELEŞTİRMEN AJAN: KÖK NEDEN ANALİZİ KALİTE DENETİMİ")
        print("="*80)
        
        branches = rca_data.get("analysis_branches", [])
        root_causes = rca_data.get("final_root_causes", [])
        
        if not branches:
            print("❌ Eleştirilecek dal bulunamadı!")
            return self._empty_review()
        
        # ADIM 1: Bütünsel çeşitlilik kontrolü
        print("\n📊 ADIM 1: Bütünsel Çeşitlilik ve Kapsam Analizi")
        print("-" * 60)
        global_critique = self._critique_global_diversity(
            branches, root_causes, incident_summary
        )
        
        # ADIM 2: Her dal için bireysel eleştiri
        print("\n🔬 ADIM 2: Dal Bazında Derinlik Analizi")
        print("-" * 60)
        branch_reviews = []
        for branch in branches:
            review = self._critique_single_branch(branch, incident_summary)
            branch_reviews.append(review)
            self._print_branch_review(review)
        
        # ADIM 3: Eksik boyut tespiti
        print("\n🧩 ADIM 3: Eksik Boyut Tespiti")
        print("-" * 60)
        missing_dimensions = self._check_missing_dimensions(
            branches, root_causes, incident_summary
        )
        
        # ADIM 4: Genel karar
        overall_score, overall_verdict = self._calculate_overall_verdict(
            global_critique, branch_reviews, missing_dimensions
        )
        
        # ADIM 5: Revizyon talimatları üret
        revision_instructions = self._generate_revision_instructions(
            global_critique, branch_reviews, missing_dimensions, overall_verdict
        )
        
        # Sonuç paketini derle
        result = {
            "overall_verdict": overall_verdict,
            "overall_score": overall_score,
            "global_critique": global_critique,
            "branch_reviews": branch_reviews,
            "missing_dimensions": missing_dimensions,
            "revision_instructions": revision_instructions,
            "approved_branches": [
                r["branch_number"] for r in branch_reviews 
                if r["verdict"] == "PASS"
            ],
            "branches_to_revise": [
                r["branch_number"] for r in branch_reviews 
                if r["verdict"] == "REVISE"
            ],
            "branches_to_reject": [
                r["branch_number"] for r in branch_reviews 
                if r["verdict"] == "REJECT"
            ]
        }
        
        self._print_final_verdict(result)
        self.critique_history.append(result)
        
        return result
    
    # ============================================================
    # ADIM 1: BÜTÜNSEL ÇEŞİTLİLİK
    # ============================================================
    
    def _critique_global_diversity(
        self, branches: List[Dict], root_causes: List[Dict], incident_summary: str
    ) -> Dict:
        """
        Tüm dalları birlikte değerlendir:
        - Kök nedenler gerçekten farklı mı?
        - İsviçre Peyniri boyutları var mı?
        - Rapordaki kritik faktörler yansıtıldı mı?
        """
        
        # Kök neden kodlarını çıkar
        rc_codes = [rc.get("code", "?") for rc in root_causes]
        rc_titles = [rc.get("standard_title_tr", "") for rc in root_causes]
        rc_categories = [rc.get("category_type", "") for rc in root_causes]
        
        # Immediate cause kodları
        imm_codes = [b["immediate_cause"].get("code", "?") for b in branches]
        
        prompt = f"""Sen kıdemli bir İSG soruşturma uzmanısın ve bir kök neden analizini kalite denetiminden geçiriyorsun.

OLAY ÖZETİ:
{incident_summary}

ÜRETİLEN ANALİZ:
Doğrudan Neden Kodları: {imm_codes}
Kök Neden Kodları: {rc_codes}
Kök Neden Başlıkları: {rc_titles}
Kök Neden Kategorileri: {rc_categories}

DAL PERSPEKTİFLERİ:
{json.dumps([{"dal": b["branch_number"], "perspektif": b.get("perspective",""), "kök_neden": b["root_cause"].get("cause_tr","")} for b in branches], ensure_ascii=False, indent=2)}

DEĞERLENDIR:

1. ÇEŞİTLİLİK PUANI (0-10):
   - Kök nedenler gerçekten FARKLI sistematik sorunları gösteriyor mu?
   - Yoksa aynı şeyi farklı kelimelerle mi söylüyor?
   - Hem C (kişisel) hem D (organizasyonel) kategorisi var mı?

2. KAPSAM PUANI (0-10):
   - Bu olayda bilinen kritik faktörler yansıtıldı mı?
   - Banksman yokluğu, PA'nın sahadan ayrılması, süpervizör müdahalesi, 
     iş izin kalitesi, OHTL sahibiyle koordinasyon eksikliği
   - Hangileri analizde YOK?

3. BOYUTLULUK PUANI (0-10):
   - İnsan faktörü (operatör psikolojisi, dikkat, stres) ele alındı mı?
   - Teknik/mühendislik boyutu (LOTO, izolasyon, bariyer) ele alındı mı?
   - Organizasyonel/kültürel boyut ele alındı mı?

JSON ÇIKTI:
{{
  "diversity_score": 7.5,
  "coverage_score": 6.0,
  "dimensionality_score": 8.0,
  "duplicate_root_causes": ["D4.1 ve D4.2 özünde aynı şeyi söylüyor"],
  "missing_critical_factors": [
    "Banksman yokluğu hiçbir dalda kök neden olarak işlenmedi",
    "PA'nın sahadan ayrılması ve görev devir sorunu yansıtılmadı"
  ],
  "missing_dimensions": ["Kişisel faktör (C kategorisi) hiç yok"],
  "strengths": ["Teknik boyut iyi işlenmiş"],
  "overall_global_score": 7.2
}}"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Sen İSG analiz kalite denetçisisin. Sadece JSON döndür."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = safe_json_parse(
            response.choices[0].message.content,
            context="Global Diversity Critique",
            default={"overall_global_score": 5.0, "missing_critical_factors": [], "duplicate_root_causes": []}
        )
        
        print(f"   Çeşitlilik Puanı    : {result.get('diversity_score', '?')}/10")
        print(f"   Kapsam Puanı        : {result.get('coverage_score', '?')}/10")
        print(f"   Boyutluluk Puanı    : {result.get('dimensionality_score', '?')}/10")
        print(f"   Genel Global Puan   : {result.get('overall_global_score', '?')}/10")
        
        if result.get("duplicate_root_causes"):
            print(f"\n   ⚠️  Tekrar Eden Kök Nedenler:")
            for d in result["duplicate_root_causes"]:
                print(f"      - {d}")
        
        if result.get("missing_critical_factors"):
            print(f"\n   ❌ Eksik Kritik Faktörler:")
            for m in result["missing_critical_factors"]:
                print(f"      - {m}")
        
        return result
    
    # ============================================================
    # ADIM 2: DAL BAZINDA ELEŞTİRİ
    # ============================================================
    
    def _critique_single_branch(self, branch: Dict, incident_summary: str) -> Dict:
        """
        Tek bir dalı 5 kritere göre puanla ve karar ver.
        """
        branch_num = branch.get("branch_number", "?")
        perspective = branch.get("perspective", "")
        immediate = branch.get("immediate_cause", {})
        whys = branch.get("why_chain", [])
        root = branch.get("root_cause", {})
        
        print(f"\n   Dal {branch_num}: {perspective}")
        
        prompt = f"""Sen İSG 5-Why analiz uzmanısın. Aşağıdaki tek dalı eleştir.

OLAY: {incident_summary}

DAL {branch_num} - {perspective}:

DOĞRUDAN NEDEN [{immediate.get('code','')}]:
{immediate.get('cause_tr','')}
Kanıt: {immediate.get('evidence_tr','')}

5-WHY ZİNCİRİ:
{json.dumps(whys, ensure_ascii=False, indent=2)}

KÖK NEDEN [{root.get('code','')}] {root.get('standard_title_tr','')}:
{root.get('cause_tr','')}
{root.get('explanation_tr','')}

5 KRİTERE GÖRE PUAN VER (her biri 0-10):

1. MANTIKSAL BÜTÜNLÜK: Why zinciri A→B→C→D şeklinde mantıksal olarak birbirine bağlı mı?
   Her Why bir öncekinin gerçek sebebini mi soruyor?

2. DERİNLEŞME KALİTESİ: Zincir gerçekten derinleşiyor mu?
   Yoksa aynı şeyi farklı kelimelerle mi söylüyor? ("X olmadı çünkü X planlanmadı" gibi döngüler)

3. KANIT DAYANAĞI: Doğrudan neden seçimi rapordaki somut kanıta dayandırılmış mı?

4. KÖK NEDEN UYGUNLUĞU: Seçilen kök neden kodu bu dala uygun mu?
   Bu perspektife (davranışsal/teknik/gözetim) mantıksal olarak bağlı mı?

5. EYLENEBİLİRLİK: Bu kök nedenden çıkarılabilecek somut, uygulanabilir bir düzeltici eylem var mı?

JSON ÇIKTI:
{{
  "branch_number": {branch_num},
  "scores": {{
    "logical_coherence": 8.0,
    "depth_quality": 5.5,
    "evidence_basis": 7.0,
    "root_cause_fit": 6.5,
    "actionability": 8.0
  }},
  "average_score": 7.0,
  "verdict": "REVISE",
  "critical_issues": [
    "Neden 3 ve Neden 4 aynı fikri tekrarlıyor: 'prosedür yok çünkü prosedür hazırlanmamış'"
  ],
  "specific_fix_instructions": [
    "Neden 3'ü şu soruyla değiştir: 'Neden supervisor müdahale etmedi?' → Otorite kullanımı veya kültürel baskı boyutunu araştır"
  ],
  "what_is_good": ["Doğrudan neden kanıtı güçlü"]
}}

Karar kriterleri: PASS≥7.0, REVISE=5.0-6.9, REJECT<5.0"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Sen 5-Why kalite denetçisisin. Sadece JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        review = safe_json_parse(
            response.choices[0].message.content,
            context=f"Branch {branch_num} Critique",
            default={
                "branch_number": branch_num,
                "scores": {},
                "average_score": 5.0,
                "verdict": "REVISE",
                "critical_issues": [],
                "specific_fix_instructions": [],
                "what_is_good": []
            }
        )
        
        # Skoru hesapla
        scores = review.get("scores", {})
        if scores:
            avg = sum(scores.values()) / len(scores)
            review["average_score"] = round(avg, 1)
        
        # Verdict belirle
        avg_score = review.get("average_score", 5.0)
        if avg_score >= PASS_THRESHOLD:
            review["verdict"] = "PASS"
        elif avg_score >= REVISE_THRESHOLD:
            review["verdict"] = "REVISE"
        else:
            review["verdict"] = "REJECT"
        
        return review
    
    def _print_branch_review(self, review: Dict):
        """Tek dal eleştirisini yazdır"""
        bn = review.get("branch_number", "?")
        verdict = review.get("verdict", "?")
        score = review.get("average_score", 0)
        
        verdict_icon = {"PASS": "✅", "REVISE": "🔧", "REJECT": "❌"}.get(verdict, "?")
        print(f"      Puan: {score}/10  Karar: {verdict_icon} {verdict}")
        
        scores = review.get("scores", {})
        if scores:
            print(f"      Mantık:{scores.get('logical_coherence','?')} | "
                  f"Derinlik:{scores.get('depth_quality','?')} | "
                  f"Kanıt:{scores.get('evidence_basis','?')} | "
                  f"Uygunluk:{scores.get('root_cause_fit','?')} | "
                  f"Eylem:{scores.get('actionability','?')}")
        
        if review.get("critical_issues"):
            for issue in review["critical_issues"][:2]:
                print(f"      ⚠️  {issue}")
    
    # ============================================================
    # ADIM 3: EKSİK BOYUT TESPİTİ
    # ============================================================
    
    def _check_missing_dimensions(
        self, branches: List[Dict], root_causes: List[Dict], incident_summary: str
    ) -> Dict:
        """
        Analizde tamamen atlanmış boyutları tespit et ve
        yeni bir dal eklenmesi gerekip gerekmediğine karar ver.
        """
        rc_codes = [rc.get("code", "") for rc in root_causes]
        has_personal = any(c.startswith("C") for c in rc_codes)
        has_org = any(c.startswith("D") for c in rc_codes)
        
        # D kodlarının sub-kategorilerini kontrol et
        d_subcats = set()
        for c in rc_codes:
            if c.startswith("D") and len(c) >= 2:
                d_subcats.add(c[:2])
        
        issues = []
        new_branch_needed = False
        new_branch_suggestion = None
        
        if not has_personal:
            issues.append({
                "type": "EKSIK_BOYUT",
                "severity": "YÜKSEK",
                "description": "C kategorisi (kişisel faktör) hiçbir kök nedende yok. Operatörün bilişsel durumu, yetkinliği veya mental stresi analiz edilmemiş.",
                "action": "YENİ_DAL_EKLE"
            })
            new_branch_needed = True
            new_branch_suggestion = {
                "perspective": "KİŞİSEL FAKTÖR - Operatör Bilişsel Durumu",
                "focus": "C kategorisi",
                "suggested_immediate_cause": "A4.1 veya A4.5 - Dikkat dağınıklığı/kasıtsız hata",
                "target_root_cause": "C2.1, C2.5 veya C3.1"
            }
        
        if "D1" not in d_subcats:
            issues.append({
                "type": "EKSIK_BOYUT", 
                "severity": "ORTA",
                "description": "D1 (Liderlik ve Güvenlik Kültürü) kategorisi yok. Süpervizörün müdahale etmemesi ve banksman yokluğu yönetsel bir kültür sorununa işaret ediyor.",
                "action": "MEVCUT_DAL_GENIŞLET"
            })
        
        if "D7" not in d_subcats:
            issues.append({
                "type": "EKSIK_BOYUT",
                "severity": "ORTA", 
                "description": "D7 (Yüklenici Yönetimi) kategorisi yok. BNT/Bonatti yüklenicisinin denetimi ve yeterlilik kontrolü ele alınmamış.",
                "action": "MEVCUT_DAL_GENIŞLET"
            })
        
        result = {
            "has_personal_factor": has_personal,
            "has_organizational_factor": has_org,
            "d_subcategories_covered": list(d_subcats),
            "issues": issues,
            "new_branch_needed": new_branch_needed,
            "new_branch_suggestion": new_branch_suggestion,
            "total_missing_count": len(issues)
        }
        
        if issues:
            print(f"   {len(issues)} eksik boyut tespit edildi:")
            for issue in issues:
                sev_icon = "🔴" if issue["severity"] == "YÜKSEK" else "🟡"
                print(f"   {sev_icon} [{issue['severity']}] {issue['description'][:80]}...")
        else:
            print("   ✅ Tüm temel boyutlar kapsanmış")
        
        if new_branch_needed:
            print(f"\n   💡 YENİ DAL ÖNERİSİ: {new_branch_suggestion['perspective']}")
        
        return result
    
    # ============================================================
    # ADIM 4: GENEL KARAR
    # ============================================================
    
    def _calculate_overall_verdict(
        self, global_critique: Dict, branch_reviews: List[Dict], missing_dimensions: Dict
    ) -> Tuple[float, str]:
        """
        Tüm skorları birleştirerek genel karar ver.
        """
        # Global skoru al
        global_score = global_critique.get("overall_global_score", 5.0)
        
        # Dal ortalama skoru
        branch_scores = [r.get("average_score", 5.0) for r in branch_reviews]
        branch_avg = sum(branch_scores) / len(branch_scores) if branch_scores else 5.0
        
        # Eksik boyut cezası
        missing_penalty = missing_dimensions.get("total_missing_count", 0) * 0.5
        
        # Kritik sorun cezası (REJECT olan dal varsa)
        rejected_count = sum(1 for r in branch_reviews if r.get("verdict") == "REJECT")
        reject_penalty = rejected_count * 1.5
        
        # Ağırlıklı ortalama
        overall = (global_score * 0.4 + branch_avg * 0.6) - missing_penalty - reject_penalty
        overall = max(0.0, min(10.0, round(overall, 1)))
        
        # Karar
        if overall >= PASS_THRESHOLD and not missing_dimensions.get("new_branch_needed"):
            verdict = "PASS"
        elif overall >= REVISE_THRESHOLD:
            verdict = "REVISE"
        else:
            verdict = "REJECT"
        
        # Herhangi bir dal REJECT ise minimum REVISE
        if rejected_count > 0 and verdict == "PASS":
            verdict = "REVISE"
        
        print(f"\n📊 GENEL SKOR HESABI:")
        print(f"   Global Skor     : {global_score}/10")
        print(f"   Dal Ortalaması  : {branch_avg:.1f}/10")
        print(f"   Eksik Ceza      : -{missing_penalty}")
        print(f"   Reject Cezası   : -{reject_penalty}")
        print(f"   ─────────────────────")
        print(f"   GENEL SKOR      : {overall}/10")
        
        return overall, verdict
    
    # ============================================================
    # ADIM 5: REVİZYON TALİMATLARI
    # ============================================================
    
    def _generate_revision_instructions(
        self, global_critique: Dict, branch_reviews: List[Dict],
        missing_dimensions: Dict, overall_verdict: str
    ) -> Dict:
        """
        Yeniden üretim için spesifik talimatlar üret.
        """
        instructions = {
            "verdict": overall_verdict,
            "branch_specific": {},
            "global_fixes": [],
            "new_branches_to_add": []
        }
        
        # Dal bazında talimatlar
        for review in branch_reviews:
            bn = review.get("branch_number")
            if review.get("verdict") in ["REVISE", "REJECT"]:
                instructions["branch_specific"][str(bn)] = {
                    "action": review["verdict"],
                    "issues": review.get("critical_issues", []),
                    "fix_instructions": review.get("specific_fix_instructions", []),
                    "target_score": PASS_THRESHOLD
                }
        
        # Global düzeltmeler
        for dup in global_critique.get("duplicate_root_causes", []):
            instructions["global_fixes"].append(
                f"TEKRAR GİDER: {dup}"
            )
        for missing in global_critique.get("missing_critical_factors", []):
            instructions["global_fixes"].append(
                f"KAPSAM EKLE: {missing}"
            )
        
        # Yeni dal ekleme
        if missing_dimensions.get("new_branch_needed"):
            suggestion = missing_dimensions.get("new_branch_suggestion", {})
            instructions["new_branches_to_add"].append({
                "perspective": suggestion.get("perspective", ""),
                "focus": suggestion.get("focus", ""),
                "instructions": f"""
Yeni bir dal ekle: {suggestion.get('perspective', '')}
- Doğrudan neden kodu: {suggestion.get('suggested_immediate_cause', '')}
- Hedef kök neden: {suggestion.get('target_root_cause', '')}
- Bu dal operatörün bireysel bilişsel faktörlerini (dikkat, hafıza, stres) araştırmalı
- 5-Why zinciri: Operatör hatası → Eğitim eksikliği? Stres? → Yetkinlik doğrulaması yok → C kategorisi kök neden
"""
            })
        
        return instructions
    
    # ============================================================
    # YARDIMCI FONKSİYONLAR
    # ============================================================
    
    def _print_final_verdict(self, result: Dict):
        """Nihai kararı yazdır"""
        verdict = result["overall_verdict"]
        score = result["overall_score"]
        
        verdict_display = {
            "PASS": "✅ KABUL - Analiz yeterli kalitede",
            "REVISE": "🔧 REVİZYON GEREKLİ - Hedefli düzeltmeler yapılmalı",
            "REJECT": "❌ RED - Analiz köklü biçimde yeniden yapılmalı"
        }.get(verdict, verdict)
        
        print("\n" + "="*80)
        print(f"🏁 ELEŞTİRMEN KARARI: {verdict_display}")
        print(f"   Genel Puan: {score}/10")
        print("="*80)
        
        approved = result.get("approved_branches", [])
        to_revise = result.get("branches_to_revise", [])
        to_reject = result.get("branches_to_reject", [])
        
        if approved:
            print(f"✅ Onaylanan Dallar   : {approved}")
        if to_revise:
            print(f"🔧 Revizyon Gereken   : {to_revise}")
        if to_reject:
            print(f"❌ Reddedilen Dallar  : {to_reject}")
        
        missing = result.get("missing_dimensions", {})
        if missing.get("new_branch_needed"):
            print(f"💡 Yeni Dal Gerekli   : {missing['new_branch_suggestion']['perspective']}")
        
        instr = result.get("revision_instructions", {})
        if instr.get("global_fixes"):
            print(f"\n📋 Global Düzeltmeler:")
            for fix in instr["global_fixes"][:3]:
                print(f"   → {fix[:80]}")
        
        print("="*80)
    
    def _empty_review(self) -> Dict:
        return {
            "overall_verdict": "REJECT",
            "overall_score": 0.0,
            "global_critique": {},
            "branch_reviews": [],
            "missing_dimensions": {},
            "revision_instructions": {},
            "approved_branches": [],
            "branches_to_revise": [],
            "branches_to_reject": []
        }
    
    def get_critique_history(self) -> List[Dict]:
        """Tüm eleştiri geçmişini döndür"""
        return self.critique_history
    
    def get_last_critique(self) -> Optional[Dict]:
        """Son eleştiriyi döndür"""
        return self.critique_history[-1] if self.critique_history else None
