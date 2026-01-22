"""
Root Cause Agent - Part 3 of HSG245
Performs 5 Why Analysis and identifies immediate, underlying, and root causes
+ RAG Integration: A/B categories for immediate causes, C/D for root causes
"""

from openai import OpenAI
from typing import Dict, List, Optional
import json
import os


class RootCauseAgent:
    """
    Part 3: Root Cause Analysis
    Implements 5 Why methodology to identify:
    - Immediate causes (A/B categories from RAG) 
    - Underlying causes (contributing factors)
    - Root causes (C/D categories from RAG)
    
    Uses AI + RAG to build causal chains and analyze incidents
    """
    
    def __init__(self):
        """Initialize Root Cause Agent with OpenRouter and RAG"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # RAG sistemi initialize et (opsiyonel)
        try:
            from shared.rag_system import get_rag_system
            self.rag = get_rag_system()
            self.use_rag = True
            print(f"✅ Kök Neden Ajanı başlatıldı (RAG aktif - Kategori bilgisi yüklü)")
        except Exception as e:
            self.rag = None
            self.use_rag = False
            print(f"✅ Kök Neden Ajanı başlatıldı (RAG olmadan)")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        Perform comprehensive root cause analysis following HSG245 methodology
        """
        print("\n" + "="*80)
        print("📋 BÖLÜM 3: KÖK NEDEN ANALİZİ - Olay Analiz Ediliyor")
        print("="*80)
        
        # Prepare incident description (with fallback)
        try:
            incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        except Exception as e:
            # --- DEĞİŞİKLİK 2: Log Türkçeleştirme ---
            print(f"⚠️ Uyarı: Tam özet hazırlanamadı ({e}). Sadece soruşturma verisi kullanılıyor.")
            # Fallback: Use only investigation data
            incident_summary = f"{investigation_data.get('how_happened', 'Olay detayı mevcut değil')}"
        
        # Initialize root cause analysis structure
        rca_data = {
            "incident_summary": incident_summary,
            "immediate_causes": [],
            "five_why_chains": [],  # One chain per immediate cause
            "underlying_causes": [],
            "root_causes": [],
            "analysis_method": "HSG245 5 Why Analysis"
        }
        
        # STEP 1: Identify immediate causes first (DeepSeek)
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme ...")
        immediate_causes = self._identify_immediate_causes(incident_summary)
        rca_data["immediate_causes"] = immediate_causes
        
        # STEP 2: For each immediate cause, perform 5 Why analysis (DeepSeek)
        print(f"\n🔗 ADIM 2: Her Doğrudan Neden için 5 Neden Analizi ({len(immediate_causes)} zincir)...")
        
        all_chains = []
        all_underlying = []
        all_root = []
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n   Zincir {idx}/{len(immediate_causes)}: {immediate_cause.get('cause_tr', immediate_cause.get('cause', ''))}...")
            
            # Perform 5 Why for this immediate cause
            chain = self._perform_5why_for_cause(immediate_cause, incident_summary)
            all_chains.append(chain)
            
            # Extract underlying and root from this chain
            underlying = self._extract_underlying_from_chain(chain)
            root = self._extract_root_from_chain(chain)
            
            all_underlying.extend(underlying)
            all_root.append(root)
        
        rca_data["five_why_chains"] = all_chains
        rca_data["underlying_causes"] = all_underlying
        rca_data["root_causes"] = all_root
        
        print("\n✅ Kök neden analizi tamamlandı!")
        
        # --- DEĞİŞİKLİK 4 (YENİ KOD): Raporu yakala ve veriye ekle ---
        try:
            # Raporu fonksiyondan alıyoruz
            final_report_text = self._generate_final_report(rca_data)
            
            # Admin panelinin okuması için sözlüğe ekliyoruz
            rca_data["final_report_tr"] = final_report_text
            
        except Exception as e:
            print(f"❌ Rapor oluşturulurken hata: {e}")
            rca_data["final_report_tr"] = "Rapor oluşturulamadı."
        
        # Veriyi döndür (Artık içinde final_report_tr var!)
        return rca_data
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                 investigation_data: Dict = None) -> str:
        """Combine all available information into incident summary"""
        # DEBUG: Check types
        print(f"🐛 DEBUG - part1_data type: {type(part1_data)}, value: {part1_data}")
        print(f"🐛 DEBUG - part2_data type: {type(part2_data)}, value: {part2_data}")
        
        summary_parts = []
        brief = part1_data.get("brief_details", {})
        if brief.get("what"): summary_parts.append(f"What happened: {brief['what']}")
        if brief.get("who"): summary_parts.append(f"Who: {brief['who']}")
        if brief.get("where"): summary_parts.append(f"Where: {brief['where']}")
        summary_parts.append(f"Event type: {part2_data.get('type_of_event', 'Unknown')}")
        summary_parts.append(f"Severity: {part2_data.get('actual_potential_harm', 'Unknown')}")
        if investigation_data:
            if investigation_data.get("equipment"): summary_parts.append(f"Equipment: {investigation_data['equipment']}")
            if investigation_data.get("additional_details"): summary_parts.append(investigation_data["additional_details"])
        return ". ".join(summary_parts)
    
    def _identify_immediate_causes(self, incident_summary: str) -> List[Dict]:
        """
        STEP 1: Identify immediate causes using AI + RAG (A/B categories)
        A: Davranışsal Nedenler (Actions)
        B: Koşullar (Conditions)
        """
        
        # RAG'den A ve B kategorilerini çek
        if self.use_rag:
            print("   📚 RAG'den A/B kategorileri çekiliyor...")
            rag_context_a = self.rag.query("A kategorisi davranışsal nedenler immediate causes actions", top_k=10)
            rag_context_b = self.rag.query("B kategorisi koşullar nedenler immediate causes conditions", top_k=10)
        else:
            # Fallback: Hardcoded örnekler
            rag_context_a = "A1.1 Bireysel kural ihlali, A1.4 Yetkisiz sapma, A2.1 Ekipman yanlış kullanım"
            rag_context_b = "B1.2 Koruyucu cihazlar arızalı, B1.6 Koruyucu sistemler devre dışı, B2.1 Ekipman arızası"
        
        prompt = f"""Sen bir İSG kaza araştırma uzmanısın. HSG245 metodolojisini kullanıyorsun.

OLAY ÖZETİ:
{incident_summary}

A KATEGORİSİ (DAVRANIŞSAL NEDENLER - Immediate Causes):
{rag_context_a}

B KATEGORİSİ (KOŞULLAR - Immediate Causes):
{rag_context_b}

GÖREV:
1. Bu olayın DOĞRUDAN NEDENLERİNİ (Immediate Causes) belirle
2. Yukarıdaki A ve B kategorilerinden en uygun olanları seç
3. Tipik olarak 2-4 doğrudan neden olur
4. Her neden için DETAYLI AÇIKLAMA yaz (neden bu bir doğrudan neden, nasıl katkıda bulundu)

CRITICAL RULES:
- KOD YAZMA! Sadece açıklama yaz. Örnek: "Operatör makineye yetkisiz müdahale etti" (✅), "A2.1 Ekipman yanlış kullanım" (❌)
- Her "cause" alanı en az 2 cümle olmalı (ne oldu + neden önemli)
- "evidence" alanında somut kanıtlar belirt

Return JSON with:
{{
  "causes": [
    {{
      "cause": "Detaylı açıklama (kod YOK, sadece açıklama)",
      "cause_tr": "Detaylı açıklama (kod YOK, sadece açıklama)",
      "evidence": "Somut kanıtlar ve gözlemler",
      "evidence_tr": "Somut kanıtlar ve gözlemler"
    }}
  ]
}}

CRITICAL: All text fields must be 100% in TURKISH language. NO CATEGORY CODES in cause field!

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are an HSG245 incident investigation expert. Return only valid JSON with ALL content in TURKISH language."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            data = json.loads(result)
            causes = data.get("causes", [])
            
            # --- YENİ: KOD TEMİZLEME ---
            import re
            for item in causes:
                # Kod pattern'i: A1.1, B2.3, vb.
                code_pattern = r'\b[ABCD]\d+(\.\d+)?\b'
                
                # cause alanından kod temizle
                if item.get("cause"):
                    original = item["cause"]
                    cleaned = re.sub(code_pattern, '', item["cause"]).strip()
                    # Başındaki ":" veya "-" varsa temizle
                    cleaned = re.sub(r'^[\s\-:]+', '', cleaned).strip()
                    item["cause"] = cleaned
                    
                    if original != cleaned:
                        print(f"      🧹 Kod temizlendi: '{original[:50]}...' → '{cleaned[:50]}...'")
                
                # cause_tr alanından da kod temizle
                if item.get("cause_tr"):
                    original_tr = item["cause_tr"]
                    cleaned_tr = re.sub(code_pattern, '', item["cause_tr"]).strip()
                    cleaned_tr = re.sub(r'^[\s\-:]+', '', cleaned_tr).strip()
                    item["cause_tr"] = cleaned_tr
            # ---------------------------
            
            # --- MEVCUT KOD: İngilizce alanları Türkçe ile değiştir ---
            for item in causes:
                # Eğer Türkçe veri varsa, ana 'cause' alanına onu yaz
                if item.get("cause_tr"):
                    item["cause"] = item["cause_tr"] 
                
                # Eğer Türkçe kanıt varsa, ana 'evidence' alanına onu yaz
                if item.get("evidence_tr"):
                    item["evidence"] = item["evidence_tr"]
            # ------------------------------------------------------------------
            
            print(f"   ✅ {len(causes)} doğrudan neden belirlendi (Türkçeleştirildi + Kod temizlendi)")
            return causes
        except json.JSONDecodeError:
            return []
    
    def _perform_5why_for_cause(self, immediate_cause: Dict, incident_summary: str) -> Dict:
        """
        STEP 2: Perform 5 Why analysis with Turkish output + RAG (C/D categories for root)
        C: Kişisel Faktörler (Personal)
        D: Organizasyonel Faktörler (Organizational)
        """
        cause_en = immediate_cause.get("cause", "")
        cause_tr = immediate_cause.get("cause_tr", "")
        
        # RAG'den C ve D kategorilerini çek (Root Causes için)
        if self.use_rag:
            rag_context_c = self.rag.query("C kategorisi kişisel faktörler personal systemic root causes", top_k=8)
            rag_context_d = self.rag.query("D kategorisi organizasyonel faktörler organizational systemic root causes", top_k=8)
        else:
            # Fallback
            rag_context_c = "C1.4 Yorgunluk, C3.1 Yetersiz beceri"
            rag_context_d = "D1.4 Üretim baskısı, D6.1 Yetersiz bakım stratejisi, D3.1 Yetersiz eğitim"
        
        prompt = f"""Sen 5-Why analizi yapan bir İSG uzmanısın. HSG245 metodolojisi kullanıyorsun.

OLAY: {incident_summary}
DOĞRUDAN NEDEN: {cause_en} ({cause_tr})

C KATEGORİSİ (KİŞİSEL FAKTÖRLER - Root Causes):
{rag_context_c}

D KATEGORİSİ (ORGANİZASYONEL FAKTÖRLER - Root Causes):
{rag_context_d}

GÖREV: 5 Neden Analizi yap - KRONOLOJİK SIRALAMA ÇOK ÖNEMLİ!

CRITICAL RULE - SIRALAMA:
- Why 1 (Level 1) → ÖNCE
- Why 2 (Level 2) → SONRA  
- Why 3 (Level 3) → SONRA
- Why 4 (Level 4) → SONRA
- Why 5 (Level 5 - ROOT) → EN SON

❌ YANLIŞ: 1→3→5→2 (kronolojik kopukluk)
✅ DOĞRU: 1→2→3→4→5 (mantıklı sıralama)

Her bir "why" bir önceki "because" cevabının nedenidir. Merdiven gibi: 1. basamaktan 2. basamağa, oradan 3. basamağa çık.

Return JSON with:
{{
  "immediate_cause": {{...}},
  "why_chain": [
    {{"level": 1, "cause_type": "immediate", "why_question": "Neden bu doğrudan neden meydana geldi?", "why_question_tr": "Neden bu doğrudan neden meydana geldi?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 2, "cause_type": "underlying", "why_question": "Neden [Level 1 cevabı] oldu?", "why_question_tr": "Neden [Level 1 cevabı] oldu?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 3, "cause_type": "underlying", "why_question": "Neden [Level 2 cevabı] oldu?", "why_question_tr": "Neden [Level 2 cevabı] oldu?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 4, "cause_type": "underlying", "why_question": "Neden [Level 3 cevabı] oldu?", "why_question_tr": "Neden [Level 3 cevabı] oldu?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 5, "cause_type": "root", "why_question": "Neden [Level 4 cevabı] oldu?", "why_question_tr": "Neden [Level 4 cevabı] oldu?", "because_answer": "... (C veya D kategorisinden)", "because_answer_tr": "... (C veya D kategorisinden)"}}
  ],
  "root_cause": {{"root": "Level 5 cevabı", "root_tr": "Level 5 cevabı"}}
}}

IMPORTANT: 
- Level 1: immediate cause (başlangıç)
- Levels 2-4: UNDERLYING CAUSES (ara nedenler - sırayla!)
- Level 5: ROOT CAUSE (kök neden - yukarıdaki C/D kategorilerinden)
- All _tr fields: 100% TURKISH
- SIRALAMAYA DİKKAT: 1→2→3→4→5 (asla atlama yapma!)

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are a 5 Why analysis expert. Return only valid JSON with all _tr fields in TURKISH language."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            chain = json.loads(result)
            
            # --- YENİ: SIRALAMA KONTROLÜ ---
            why_chain = chain.get("why_chain", [])
            if why_chain:
                # Sıralama kontrolü: level değerleri 1, 2, 3, 4, 5 olmalı
                expected_levels = [1, 2, 3, 4, 5]
                actual_levels = [step.get("level", 0) for step in why_chain]
                
                if actual_levels != expected_levels:
                    print(f"      ⚠️ UYARI: Sıralama hatası tespit edildi!")
                    print(f"         Beklenen: {expected_levels}")
                    print(f"         Gelen: {actual_levels}")
                    print(f"      🔧 Düzeltiliyor...")
                    
                    # Sıralamayı düzelt
                    for i, step in enumerate(why_chain, 1):
                        step["level"] = i
                        if i == 1:
                            step["cause_type"] = "immediate"
                        elif i == 5:
                            step["cause_type"] = "root"
                        else:
                            step["cause_type"] = "underlying"
                    
                    print(f"      ✅ Sıralama düzeltildi: 1→2→3→4→5")
            # -----------------------------------
            
            # --- MEVCUT KOD: Zinciri Türkçeleştir ---
            # 1. Zincirdeki (Why 1, Why 2...) soruları ve cevapları değiştir
            for step in chain.get("why_chain", []):
                if step.get("why_question_tr"):
                    step["why_question"] = step["why_question_tr"]
                
                if step.get("because_answer_tr"):
                    step["because_answer"] = step["because_answer_tr"]
            
            # 2. Kök Nedeni (Root Cause) değiştir
            root = chain.get("root_cause", {})
            if isinstance(root, dict):
                if root.get("root_tr"):
                    root["root"] = root["root_tr"]
                print(f"      Kok: {root.get('root', 'N/A')}")
            else:
                # Bazen string gelebilir, onu da handle edelim
                pass 
            # ------------------------------------------------
            
            return chain
        except json.JSONDecodeError:
            return {"immediate_cause": immediate_cause, "why_chain": [], "root_cause": {}}
    
    def _generate_final_report(self, rca_data: Dict) -> str:
        """
        FINAL EDITOR: Generate professional Turkish report
        """
        print("\nFinal Rapor Hazirlanyor (Profesyonel Rapor Modu)...")
        
        raw_data_str = json.dumps(rca_data, indent=2, ensure_ascii=False)
        
        prompt = f"""You are a professional Occupational Health and Safety Report Editor.

INPUT DATA (AI-generated analysis):
{raw_data_str}

TASK:
Based on this data, write a professional, formal 'Root Cause Analysis Report'.

MANDATORY REQUIREMENTS:
1. Language: ONLY TURKISH (no English words!)
2. Tone: Formal, objective, senior safety expert style
3. Structure:
   - YONETICI OZETI (Executive Summary)
   - OLAY DETAYLARI (Incident Details)
   - DOGRUDAN NEDENLER (Immediate Causes - list all immediate causes from input)
   - KOK NEDEN ANALIZI (For each immediate cause, explain the 5 Why chain in detail)
   - TEMEL NEDENLER (Underlying Causes - all level 2-4 causes)
   - SISTEMIK BULGULAR (Root Causes - level 5 causes)
   - SONUC VE ONERILER (Conclusion and Recommendations)
4. Format: Clean, organized text (not JSON)
5. Fix any poor translations in input data, fill logic gaps

CRITICAL: Report must be 100% in TURKISH language. Absolutely NO English words allowed in the output."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free", 
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a senior Occupational Health and Safety Expert working in Turkey. You write ALL reports in TURKISH language. You never use English."},
                {"role": "user", "content": prompt}
            ]
        )
        
        report_content = response.choices[0].message.content
        
        print("\n" + "="*80)
        print(report_content)
        print("="*80)
        
        return report_content

    # Helper methods (extract_underlying, extract_root) stay the same...
    def _extract_underlying_from_chain(self, chain: Dict) -> List[Dict]:
        underlying = []
        for why in chain.get("why_chain", []):
            if why.get("cause_type") == "underlying":
                # Önceliği Türkçeye veriyoruz
                cause_text = why.get("because_answer_tr") or why.get("because_answer", "")
                
                underlying.append({
                    "cause": cause_text,     # Artık burası kesin Türkçe
                    "cause_tr": cause_text,  # Yedek olarak kalsın
                    "level": why.get("level", 0)
                })
        return underlying
    
    def _extract_root_from_chain(self, chain: Dict) -> Dict:
        for why in chain.get("why_chain", []):
            if why.get("level") == 5 or why.get("cause_type") == "root":
                # Önceliği Türkçeye veriyoruz
                cause_text = why.get("because_answer_tr") or why.get("because_answer", "")
                
                return {
                    "cause": cause_text,    # Artık burası kesin Türkçe
                    "cause_tr": cause_text
                }
        
        # Eğer zincirden bulunamazsa root_cause objesine bak
        root_obj = chain.get("root_cause", {})
        if isinstance(root_obj, dict):
             root_text = root_obj.get("root_tr") or root_obj.get("root", "")
             return {"cause": root_text, "cause_tr": root_text}
             
        return chain.get("root_cause", {})

    def _print_summary(self, rca_data: Dict):
        # Bu fonksiyon artık kullanılmıyor ama eski loglar için tutulabilir.
        pass
