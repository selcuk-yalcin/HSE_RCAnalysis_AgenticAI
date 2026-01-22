"""
Root Cause Agent - Part 3 of HSG245 (AGENTIC AI)
Multi-step reasoning with validation loops
"""

from openai import OpenAI
from typing import Dict, List, Tuple
import json
import os
import re

# Basit bilgi tabanından kategori okuma
from shared.knowledge_base import HSG245_TAXONOMY, get_category_text


class RootCauseAgent:
    """
    Part 3: Root Cause Analysis (AGENTIC YAPISI)
    
    Agent Pipeline:
    1. Planning Agent → Analiz stratejisi belirle
    2. Search Agent → Kategorilerden neden bul
    3. Validation Agent → Bulunanları doğrula (loop)
    4. Reasoning Agent → 5-Why zinciri kur
    5. Synthesis Agent → Final rapor oluştur
    """
    
    def __init__(self):
        """Initialize Agentic Root Cause Agent"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.max_iterations = 3  # Validation loop max iterations
        print(f"✅ Kök Neden Ajanı başlatıldı (AGENTIC AI - Multi-Step Reasoning)")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        AGENTIC ANALYSIS Pipeline:
        Agent 1: Planning → Strateji belirle
        Agent 2-3: Search + Validation Loop → Immediate causes
        Agent 4: Reasoning → 5-Why chains
        Agent 5: Synthesis → Final report
        """
        print("\n" + "="*80)
        print("🤖 AGENTİC KÖK NEDEN ANALİZİ - Multi-Step Reasoning")
        print("="*80)
        
        # Olay özeti hazırla
        try:
            incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        except Exception as e:
            print(f"⚠️ Uyarı: Tam özet hazırlanamadı ({e})")
            incident_summary = investigation_data.get('how_happened', 'Olay detayı mevcut değil') if investigation_data else 'Detay yok'
        
        # Analiz yapısı
        rca_data = {
            "incident_summary": incident_summary,
            "analysis_plan": {},
            "immediate_causes": [],
            "five_why_chains": [],
            "underlying_causes": [],
            "root_causes": [],
            "analysis_method": "Agentic AI - Multi-Step Reasoning with Validation Loops"
        }
        
        # AGENT 1: Planning - Analiz stratejisi
        print("\n🧠 AGENT 1: Planning Agent - Analiz stratejisi belirleniyor...")
        rca_data["analysis_plan"] = self._planning_agent(incident_summary)
        
        # AGENT 2-3: Search + Validation Loop
        print("\n🔍 AGENT 2-3: Search + Validation Loop (Immediate Causes)...")
        immediate_causes = self._search_validate_loop(
            incident=incident_summary,
            categories=['A', 'B'],
            agent_name="Immediate Cause",
            expected_count=rca_data["analysis_plan"].get("expected_immediate_count", 3)
        )
        rca_data["immediate_causes"] = immediate_causes
        
        # AGENT 4: Reasoning - 5 Why chains
        print(f"\n🧩 AGENT 4: Reasoning Agent - {len(immediate_causes)} zincir için 5-Why analizi...")
        
        all_chains = []
        all_underlying = []
        all_root = []
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"   Zincir {idx}/{len(immediate_causes)}: {immediate_cause.get('cause', '')[:60]}...")
            
            chain = self._reasoning_agent_5why(immediate_cause, incident_summary)
            all_chains.append(chain)
            
            # Underlying ve root çıkar
            underlying = self._extract_underlying_from_chain(chain)
            root = self._extract_root_from_chain(chain)
            
            all_underlying.extend(underlying)
            all_root.append(root)
        
        rca_data["five_why_chains"] = all_chains
        rca_data["underlying_causes"] = all_underlying
        rca_data["root_causes"] = all_root
        
        # AGENT 5: Synthesis - Final report
        print("\n📝 AGENT 5: Synthesis Agent - Final rapor oluşturuluyor...")
        try:
            rca_data["final_report_tr"] = self._synthesis_agent(rca_data)
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {e}")
            rca_data["final_report_tr"] = "Rapor oluşturulamadı."
        
        print("\n✅ Agentic analiz tamamlandı!")
        return rca_data
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                 investigation_data: Dict = None) -> str:
        """Olay özetini birleştir"""
        summary_parts = []
        brief = part1_data.get("brief_details", {})
        
        if brief.get("what"): summary_parts.append(f"Ne oldu: {brief['what']}")
        if brief.get("who"): summary_parts.append(f"Kim: {brief['who']}")
        if brief.get("where"): summary_parts.append(f"Nerede: {brief['where']}")
        
        summary_parts.append(f"Olay türü: {part2_data.get('type_of_event', 'Bilinmiyor')}")
        summary_parts.append(f"Şiddet: {part2_data.get('actual_potential_harm', 'Bilinmiyor')}")
        
        if investigation_data:
            if investigation_data.get("how_happened"): 
                summary_parts.append(f"Detay: {investigation_data['how_happened']}")
        
        return ". ".join(summary_parts)
    
    # ==================== AGENT 1: PLANNING ====================
    def _planning_agent(self, incident: str) -> Dict:
        """
        AGENT 1: Analiz Planlama
        - Hangi kategorilerden ne kadar neden beklendiğini tahmin et
        - Dominant category'yi belirle
        - Root cause tipini öngör
        """
        prompt = f"""Sen bir analiz planlama uzmanısın.

OLAY: {incident}

GÖREV: Bu olayı analiz etmeden önce bir strateji belirle:
1. Kaç tane immediate cause bulmamız gerekir? (genelde 2-4)
2. Dominant category hangisi olmalı? (A: Davranışsal mı, B: Koşullar mı?)
3. Root cause'lar kişisel mi (C) organizasyonel mi (D) olacak?

JSON dön:
{{
  "expected_immediate_count": 3,
  "dominant_category": "A veya B",
  "expected_root_category": "C veya D",
  "reasoning": "Neden bu stratejiyi seçtin?"
}}

SADECE JSON dön!"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = self._extract_json(response.choices[0].message.content)
        print(f"   Plan: {result.get('reasoning', 'N/A')[:100]}...")
        print(f"   Beklenen: {result.get('expected_immediate_count', '?')} immediate cause")
        print(f"   Dominant: {result.get('dominant_category', '?')}")
        return result
    
    # ==================== AGENT 2-3: SEARCH + VALIDATION LOOP ====================
    def _search_validate_loop(self, incident: str, categories: List[str], 
                             agent_name: str, expected_count: int = 3) -> List[Dict]:
        """
        AGENT 2-3: Search + Validation Loop
        
        Agentic özellik: Validation başarısız olursa feedback ile tekrar dene!
        """
        print(f"   Başlıyor: {agent_name} (Beklenen: {expected_count} neden)")
        
        feedback_context = ""
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"   🔄 Iteration {iteration}/{self.max_iterations}")
            
            # SEARCH
            causes = self._search_agent(incident + feedback_context, categories)
            
            # VALIDATE
            is_valid, feedback = self._validation_agent(causes, incident, expected_count)
            
            if is_valid:
                print(f"   ✅ Validation PASSED! {len(causes)} neden bulundu.")
                return causes
            else:
                print(f"   ⚠️ Validation FAILED: {feedback}")
                # Feedback'i sonraki iterasyona ekle (Agentic loop!)
                feedback_context = f"\n\nÖNCEKİ DENEME FEEDBACK:\n{feedback}\nBu feedback'e göre düzelt!"
        
        # Max iteration ulaşıldı
        print(f"   ⚠️ Max iteration ulaşıldı. Son sonuç kullanılıyor ({len(causes)} neden)")
        return causes
    
    def _search_agent(self, incident: str, categories: List[str]) -> List[Dict]:
        """AGENT 2: Search - Kategorilerden neden bul"""
        category_texts = "\n\n".join([get_category_text(cat) for cat in categories])
        
        prompt = f"""İSG Uzmanı olarak analiz et.

OLAY: {incident}

KATEGORİLER:
{category_texts}

GÖREV: Doğrudan nedenleri bul (2-4 tane).

KURALLAR:
- KOD YAZMA! Sadece açıklama
- En az 2 cümle per neden
- Somut kanıt belirt

JSON:
{{
  "causes": [
    {{"cause": "detaylı açıklama", "cause_tr": "detaylı açıklama", "evidence": "kanıt", "evidence_tr": "kanıt"}}
  ]
}}

SADECE JSON!"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = self._extract_json(response.choices[0].message.content)
        causes = result.get("causes", [])
        
        # Kod temizleme (korundu)
        self._clean_category_codes(causes)
        
        return causes
    
    def _validation_agent(self, causes: List[Dict], incident: str, 
                         expected_count: int) -> Tuple[bool, str]:
        """
        AGENT 3: Validation - Bulunan nedenleri doğrula
        
        Returns: (is_valid: bool, feedback: str)
        """
        if not causes:
            return False, "Hiç neden bulunamadı!"
        
        prompt = f"""Sen bir kalite kontrol uzmanısın.

OLAY: {incident}

BULUNAN NEDENLER ({len(causes)} adet):
{json.dumps(causes, ensure_ascii=False, indent=2)}

BEKLENEN SAYI: {expected_count}

KONTROL LİSTESİ:
1. ✓ Neden sayısı uygun mu? ({len(causes)} vs {expected_count})
2. ✓ Her neden en az 2 cümle mi?
3. ✓ Kod içeriyor mu? (A1.1, B2.3 gibi - OLMAMALI!)
4. ✓ Olayla alakalı mı?
5. ✓ Kanıt var mı?

JSON dön:
{{
  "valid": true/false,
  "feedback": "Eğer geçersizse ne eksik? Nasıl düzeltilmeli?"
}}

SADECE JSON!"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = self._extract_json(response.choices[0].message.content)
        return result.get("valid", False), result.get("feedback", "Doğrulama başarısız")
    
    # ==================== AGENT 4: REASONING (5-WHY) ====================
    def _reasoning_agent_5why(self, immediate_cause: Dict, incident: str) -> Dict:
        """
        AGENT 4: 5-Why Reasoning
        - Doğrudan nedenden başla
        - 5 adımlık neden-sonuç zinciri kur
        - Root cause'u C/D kategorilerinden seç
        """
        cause_text = immediate_cause.get("cause", "")
        
        # C ve D kategorilerini al
        category_c = get_category_text('C')
        category_d = get_category_text('D')
        
        prompt = f"""5-Why analizi uzmanı olarak çalış.

OLAY: {incident}
DOĞRUDAN NEDEN: {cause_text}

KÖK NEDEN KATEGORİLERİ:
{category_c}

{category_d}

GÖREV: 5-Why zinciri kur

CRITICAL - SIRALAMA:
1→2→3→4→5 (kronolojik sıra!)

JSON:
{{
  "immediate_cause": {{"cause": "{cause_text}", "cause_tr": "{cause_text}"}},
  "why_chain": [
    {{"level": 1, "cause_type": "immediate", "why_question": "Neden?", "why_question_tr": "Neden?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 2, "cause_type": "underlying", "why_question": "Neden?", "why_question_tr": "Neden?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 3, "cause_type": "underlying", "why_question": "Neden?", "why_question_tr": "Neden?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 4, "cause_type": "underlying", "why_question": "Neden?", "why_question_tr": "Neden?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 5, "cause_type": "root", "why_question": "Neden?", "why_question_tr": "Neden?", "because_answer": "C/D kategorisinden", "because_answer_tr": "C/D kategorisinden"}}
  ],
  "root_cause": {{"root": "Level 5 cevabı", "root_tr": "Level 5 cevabı"}}
}}

TÜRKÇE! SADECE JSON!"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = self._extract_json(response.choices[0].message.content)
        
        # Sıralama kontrolü ve düzeltme
        why_chain = result.get("why_chain", [])
        self._fix_chain_order(why_chain)
        
        # Türkçeleştirme
        self._turkcelestir_chain(why_chain)
        
        # Root cause Türkçeleştir
        root = result.get("root_cause", {})
        if isinstance(root, dict) and root.get("root_tr"):
            root["root"] = root["root_tr"]
            print(f"      ✓ Kök: {root.get('root', '')[:50]}...")
        
        return result
    
    # ==================== AGENT 5: SYNTHESIS (FINAL REPORT) ====================
    def _synthesis_agent(self, rca_data: Dict) -> str:
        """
        AGENT 5: Synthesis - Final rapor oluştur
        
        Tüm agent çıktılarını birleştirip profesyonel rapor yaz
        """
        raw_data_str = json.dumps(rca_data, indent=2, ensure_ascii=False)
        
        prompt = f"""HSG245 Rapor Editörü olarak çalış.

AGENTIC ANALYSIS SONUÇLARI:
{raw_data_str}

GÖREV: Profesyonel kök neden analiz raporu yaz (TÜRKÇE)

YAPI:
- YÖNETİCİ ÖZETİ
- ANALİZ STRATEJİSİ (Planning agent sonucu)
- DOĞRUDAN NEDENLER (Search agent sonucu)
- 5-WHY ZİNCİRLERİ (Reasoning agent sonucu)
- KÖK NEDENLER
- SİSTEMİK BULGULAR
- ÖNERİLER

KURAL: SADECE TÜRKÇE! Formal üslup.

Rapor metni döndür (JSON değil!)."""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        report = response.choices[0].message.content
        print(f"   ✅ Rapor oluşturuldu ({len(report)} karakter)")
        return report
    
    # ==================== HELPER METHODS ====================
    def _extract_json(self, text: str) -> Dict:
        """JSON çıkar (markdown temizleme ile)"""
        text = text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"      ⚠️ JSON parse hatası: {e}")
            return {}
    
    def _clean_category_codes(self, causes: List[Dict]):
        """Kategori kodlarını temizle (A1.1, B2.3, vb.)"""
        code_pattern = r'\b[ABCD]\d+(\.\d+)?\b'
        
        for item in causes:
            if item.get("cause"):
                original = item["cause"]
                cleaned = re.sub(code_pattern, '', item["cause"]).strip()
                cleaned = re.sub(r'^[\s\-:]+', '', cleaned).strip()
                item["cause"] = cleaned
                
                if original != cleaned:
                    print(f"      🧹 Kod temizlendi")
            
            if item.get("cause_tr"):
                cleaned_tr = re.sub(code_pattern, '', item["cause_tr"]).strip()
                cleaned_tr = re.sub(r'^[\s\-:]+', '', cleaned_tr).strip()
                item["cause_tr"] = cleaned_tr
            
            # Türkçe → Ana alan
            if item.get("cause_tr"):
                item["cause"] = item["cause_tr"]
            if item.get("evidence_tr"):
                item["evidence"] = item["evidence_tr"]
    
    def _fix_chain_order(self, chain: List[Dict]):
        """Zincir sırasını düzelt (1→2→3→4→5)"""
        expected_levels = [1, 2, 3, 4, 5]
        actual_levels = [step.get("level", 0) for step in chain]
        
        if actual_levels != expected_levels:
            print(f"      ⚠️ Sıralama hatası - Düzeltiliyor...")
            for i, step in enumerate(chain, 1):
                step["level"] = i
                if i == 1:
                    step["cause_type"] = "immediate"
                elif i == 5:
                    step["cause_type"] = "root"
                else:
                    step["cause_type"] = "underlying"
            print(f"      ✅ Düzeltildi: 1→2→3→4→5")
    
    def _turkcelestir_chain(self, chain: List[Dict]):
        """Zinciri Türkçeleştir"""
        for step in chain:
            if step.get("why_question_tr"):
                step["why_question"] = step["why_question_tr"]
            if step.get("because_answer_tr"):
                step["because_answer"] = step["because_answer_tr"]
    
    def _extract_underlying_from_chain(self, chain: Dict) -> List[Dict]:
        """Level 2-4'ü underlying olarak çıkar"""
        underlying = []
        for why in chain.get("why_chain", []):
            if why.get("cause_type") == "underlying":
                cause_text = why.get("because_answer_tr") or why.get("because_answer", "")
                underlying.append({
                    "cause": cause_text,
                    "cause_tr": cause_text,
                    "level": why.get("level", 0)
                })
        return underlying
    
    def _extract_root_from_chain(self, chain: Dict) -> Dict:
        """Level 5'i root cause olarak çıkar"""
        for why in chain.get("why_chain", []):
            if why.get("level") == 5 or why.get("cause_type") == "root":
                cause_text = why.get("because_answer_tr") or why.get("because_answer", "")
                return {
                    "cause": cause_text,
                    "cause_tr": cause_text
                }
        
        # Fallback: root_cause objesinden al
        root_obj = chain.get("root_cause", {})
        if isinstance(root_obj, dict):
            root_text = root_obj.get("root_tr") or root_obj.get("root", "")
            return {"cause": root_text, "cause_tr": root_text}
        
        return chain.get("root_cause", {})
