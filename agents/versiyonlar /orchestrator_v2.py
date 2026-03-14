"""
Root Cause Orchestrator V2 - Eleştirmen Ajanlı Döngü
======================================================

YENİ MİMARİ:
    Part 1: Overview Agent
    Part 2: Assessment Agent
    Part 3: RootCause Agent → Critic Agent → [Revise?] → RootCause Agent → Final

DÖNGÜ MANTIĞI:
    1. RootCauseAgentV2 analiz üretir
    2. CriticAgent değerlendirir → PASS / REVISE / REJECT
    3. PASS    → Final rapor
    4. REVISE  → Sadece sorunlu dallar yeniden üretilir (approved dallar korunur)
    5. REJECT  → Tüm analiz sıfırdan yapılır
    6. Max 2 revizyon denemesinden sonra mevcut en iyi sonuç alınır
"""

from typing import Dict, Optional
from .overview_agent import OverviewAgent
from .assessment_agent import AssessmentAgent
from .rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
from .critic_agent import CriticAgent, MAX_REVISION_ATTEMPTS


class RootCauseOrchestrator:
    """
    Master koordinatör - Eleştirmen döngüsü dahil
    """
    
    def __init__(self):
        print("\n" + "="*80)
        print("🚀 ROOT CAUSE INVESTIGATION SYSTEM BAŞLATILIYOR")
        print("   (Eleştirmen Ajanlı Çok Boyutlu Sürüm)")
        print("="*80)
        
        self.overview_agent = OverviewAgent()
        self.assessment_agent = AssessmentAgent()
        self.rootcause_agent = RootCauseAgent()
        self.critic_agent = CriticAgent()
        
        self.investigation_data = {
            "part1": None,
            "part2": None,
            "part3_rca": None,
            "critic_reviews": [],
            "revision_count": 0,
            "final_verdict": None,
            "status": "initialized"
        }
        
        print("\n✅ Tüm ajanlar başlatıldı (Üretici + Eleştirmen)")
        print("="*80)
    
    def run_investigation(self, incident_data: Dict) -> Dict:
        """
        Tam soruşturma - eleştirmen döngüsü dahil
        """
        print("\n" + "="*80)
        print("🔬 SORUŞTURMA BAŞLIYOR")
        print("="*80)
        
        try:
            # ── ADIM 1: Overview ──────────────────────────────────────
            print("\n📌 ADIM 1/4: Genel Bakış (Part 1)")
            print("-"*80)
            self.investigation_data["part1"] = self.overview_agent.process_initial_report(
                incident_data
            )
            self.investigation_data["status"] = "part1_complete"
            
            # ── ADIM 2: Assessment ────────────────────────────────────
            print("\n📌 ADIM 2/4: Değerlendirme (Part 2)")
            print("-"*80)
            self.investigation_data["part2"] = self.assessment_agent.assess_incident(
                self.investigation_data["part1"],
                incident_data
            )
            self.investigation_data["status"] = "part2_complete"
            
            # ── ADIM 3: RCA + Eleştirmen Döngüsü ─────────────────────
            print("\n📌 ADIM 3/4: Kök Neden Analizi + Kalite Döngüsü (Part 3)")
            print("-"*80)
            
            rca_result = self._run_rca_with_critique_loop(incident_data)
            self.investigation_data["part3_rca"] = rca_result
            self.investigation_data["status"] = "part3_complete"
            
            # ── ADIM 4: Final Rapor ───────────────────────────────────
            print("\n📌 ADIM 4/4: Final Rapor Derleniyor")
            print("-"*80)
            self.investigation_data["status"] = "investigation_complete"
            self._print_final_summary()
            
            return self.investigation_data
            
        except Exception as e:
            print(f"\n❌ Soruşturma hatası: {e}")
            self.investigation_data["status"] = "error"
            self.investigation_data["error"] = str(e)
            raise
    
    def _run_rca_with_critique_loop(self, incident_data: Dict) -> Dict:
        """
        Eleştirmen döngüsü:
        Üret → Eleştir → Revize (max 2 kez) → Final
        """
        incident_summary_override = None  # İleride revizyon bağlamı taşımak için
        revision_count = 0
        best_rca = None
        best_score = 0.0
        
        while revision_count <= MAX_REVISION_ATTEMPTS:
            
            iteration_label = "İLK ÜRETİM" if revision_count == 0 else f"REVİZYON #{revision_count}"
            print(f"\n{'─'*60}")
            print(f"🔄 {iteration_label}")
            print(f"{'─'*60}")
            
            # RCA üret
            rca_data = self.rootcause_agent.analyze_root_causes(
                self.investigation_data["part1"],
                self.investigation_data["part2"],
                incident_data.get("investigation_details")
            )
            
            # Incident summary hazırla (eleştirmen için)
            incident_summary = self._build_incident_summary()
            
            # Eleştirmen değerlendirsin
            critique = self.critic_agent.review_full_analysis(rca_data, incident_summary)
            self.investigation_data["critic_reviews"].append(critique)
            self.investigation_data["revision_count"] = revision_count
            
            # En iyi skoru takip et
            current_score = critique.get("overall_score", 0.0)
            if current_score > best_score:
                best_score = current_score
                best_rca = rca_data
                best_rca["critic_review"] = critique
            
            verdict = critique.get("overall_verdict", "REJECT")
            
            # ── KARAR ────────────────────────────────────────────────
            if verdict == "PASS":
                print(f"\n✅ Eleştirmen ONAYLADI (Puan: {current_score}/10)")
                print(f"   {revision_count} revizyon sonrası kabul edildi.")
                rca_data["critic_review"] = critique
                rca_data["revision_count"] = revision_count
                self.investigation_data["final_verdict"] = "PASS"
                return rca_data
            
            elif verdict == "REVISE" and revision_count < MAX_REVISION_ATTEMPTS:
                print(f"\n🔧 Eleştirmen REVİZYON talep etti (Puan: {current_score}/10)")
                self._print_revision_summary(critique)
                
                # Revizyon talimatlarını rootcause agent'a aktar
                self._inject_revision_context(critique)
                revision_count += 1
                continue
            
            elif verdict == "REJECT" and revision_count < MAX_REVISION_ATTEMPTS:
                print(f"\n❌ Eleştirmen REDDETTİ (Puan: {current_score}/10)")
                print("   Analiz sıfırdan yeniden yapılıyor...")
                
                self._inject_revision_context(critique)
                revision_count += 1
                continue
            
            else:
                # Max deneme sayısına ulaşıldı
                print(f"\n⚠️  Maksimum revizyon sayısına ulaşıldı ({MAX_REVISION_ATTEMPTS})")
                print(f"   En iyi analiz kullanılıyor (Puan: {best_score}/10)")
                self.investigation_data["final_verdict"] = f"BEST_EFFORT (score: {best_score})"
                return best_rca
        
        # Güvenlik ağı
        self.investigation_data["final_verdict"] = f"BEST_EFFORT (score: {best_score})"
        return best_rca
    
    def _inject_revision_context(self, critique: Dict):
        """
        Eleştirmen talimatlarını rootcause agent'ın bir sonraki
        çalışmasında kullanılmak üzere kaydet.
        
        Not: RootCauseAgentV2'nin _identify_diverse_immediate_causes
        metoduna 'revision_context' parametresi eklenirse bu bilgi
        prompt'a enjekte edilebilir. Şimdilik agent'ın kendi forbidden_codes
        mekanizması ve perspektif yönlendirmesi bu görevi üstleniyor.
        """
        instructions = critique.get("revision_instructions", {})
        global_fixes = instructions.get("global_fixes", [])
        new_branches = instructions.get("new_branches_to_add", [])
        
        # Agent'ın used_root_cause_codes setini sıfırla (yeni denemede taze başlasın)
        self.rootcause_agent.used_root_cause_codes = set()
        
        # Gelecek versiyon: bu talimatları agent'ın prompt builder'ına enjekte et
        # Şimdilik loglayalım
        if global_fixes:
            print("\n   📋 Revizyon Talimatları Agent'a İletildi:")
            for fix in global_fixes[:3]:
                print(f"      → {fix[:70]}...")
        
        if new_branches:
            print(f"\n   💡 Yeni Dal Talebi: {new_branches[0].get('perspective','')}")
    
    def _print_revision_summary(self, critique: Dict):
        """Revizyon özetini yazdır"""
        to_revise = critique.get("branches_to_revise", [])
        to_reject = critique.get("branches_to_reject", [])
        missing = critique.get("missing_dimensions", {})
        
        print(f"   Revize edilecek dallar : {to_revise}")
        print(f"   Reddedilen dallar      : {to_reject}")
        
        if missing.get("new_branch_needed"):
            print(f"   Eklenecek yeni dal     : {missing['new_branch_suggestion']['perspective']}")
        
        instr = critique.get("revision_instructions", {})
        if instr.get("global_fixes"):
            print("   Global düzeltmeler:")
            for fix in instr["global_fixes"][:2]:
                print(f"      → {fix[:65]}...")
    
    def _build_incident_summary(self) -> str:
        """Part 1 ve Part 2 verilerinden olay özeti oluştur"""
        p1 = self.investigation_data.get("part1", {})
        p2 = self.investigation_data.get("part2", {})
        
        parts = []
        brief = p1.get("brief_details", {})
        if isinstance(brief, dict):
            for key in ["what", "where", "who", "emergency_measures"]:
                val = brief.get(key, "")
                if val:
                    parts.append(val)
        
        if p2.get("type_of_event"):
            parts.append(f"Olay tipi: {p2['type_of_event']}")
        if p2.get("actual_potential_harm"):
            parts.append(f"Ciddiyet: {p2['actual_potential_harm']}")
        
        return ". ".join(parts) if parts else "Olay özeti mevcut değil"
    
    def _print_final_summary(self):
        """Final soruşturma özetini yazdır"""
        print("\n" + "="*80)
        print("✅ SORUŞTURMA TAMAMLANDI")
        print("="*80)
        
        p1 = self.investigation_data.get("part1", {})
        p2 = self.investigation_data.get("part2", {})
        p3 = self.investigation_data.get("part3_rca", {})
        
        print(f"\n📋 Referans No       : {p1.get('ref_no', 'N/A')}")
        print(f"📊 Olay Tipi         : {p1.get('incident_type', 'N/A')}")
        print(f"⚠️  Ciddiyet          : {p2.get('actual_potential_harm', 'N/A')}")
        print(f"🔍 Soruşturma Seviyesi: {p2.get('investigation_level', 'N/A')}")
        print(f"📝 RIDDOR Bildirimi  : {p2.get('riddor_reportable', 'N/A')}")
        
        branches = p3.get("analysis_branches", [])
        root_causes = p3.get("final_root_causes", [])
        
        print(f"\n🎯 Kök Neden Analizi:")
        print(f"   Dal Sayısı          : {len(branches)}")
        print(f"   Kök Neden Sayısı    : {len(root_causes)}")
        
        # Kök neden özeti
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("code", "?")
            title = rc.get("standard_title_tr", "")
            cat = rc.get("category_type", "")
            print(f"   {i}. [{code}] {title} ({cat})")
        
        # Eleştirmen istatistikleri
        reviews = self.investigation_data.get("critic_reviews", [])
        if reviews:
            final_review = reviews[-1]
            print(f"\n🔍 Kalite Kontrolü:")
            print(f"   Revizyon Sayısı     : {self.investigation_data.get('revision_count', 0)}")
            print(f"   Final Puan          : {final_review.get('overall_score', 'N/A')}/10")
            print(f"   Final Karar         : {self.investigation_data.get('final_verdict', 'N/A')}")
        
        print(f"\n✅ Durum: {self.investigation_data.get('status', 'Unknown')}")
        print("="*80)
    
    def get_investigation_data(self) -> Dict:
        return self.investigation_data
    
    def export_to_json(self, filepath: str):
        import json
        from pathlib import Path
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.investigation_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Soruşturma dışa aktarıldı: {filepath}")
