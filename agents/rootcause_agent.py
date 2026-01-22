"""
Root Cause Agent - Part 3 of HSG245 (Simplified - No RAG)
Doğrudan Knowledge Base'den okuyarak analiz yapar.
"""

from openai import OpenAI
from typing import Dict, List
import json
import os
import re

# Basit bilgi tabanından kategori okuma
from shared.knowledge_base import HSG245_TAXONOMY, get_category_text


class RootCauseAgent:
    """
    Part 3: Root Cause Analysis (Basitleştirilmiş Yapı)
    - RAG/Veritabanı gerektirmez
    - Doğrudan HSG245 taksonomisini LLM'e gönderir
    - Hızlı ve güvenilir
    """
    
    def __init__(self):
        """Initialize Root Cause Agent"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print(f"✅ Kök Neden Ajanı başlatıldı (Basit Bilgi Tabanı Modu - No RAG)")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        HSG245 Kök Neden Analizi
        """
        print("\n" + "="*80)
        print("📋 BÖLÜM 3: KÖK NEDEN ANALİZİ")
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
            "immediate_causes": [],
            "five_why_chains": [],
            "underlying_causes": [],
            "root_causes": [],
            "analysis_method": "HSG245 5 Why Analysis (Simplified)"
        }
        
        # ADIM 1: Doğrudan Nedenler (A/B kategorileri)
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme (A/B)...")
        immediate_causes = self._identify_immediate_causes(incident_summary)
        rca_data["immediate_causes"] = immediate_causes
        
        # ADIM 2: 5 Why Analizi (C/D kategorileri)
        print(f"\n🔗 ADIM 2: {len(immediate_causes)} neden için 5-Why analizi...")
        
        all_chains = []
        all_underlying = []
        all_root = []
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"   Zincir {idx}/{len(immediate_causes)}: {immediate_cause.get('cause', '')[:60]}...")
            
            chain = self._perform_5why_for_cause(immediate_cause, incident_summary)
            all_chains.append(chain)
            
            # Underlying ve root çıkar
            underlying = self._extract_underlying_from_chain(chain)
            root = self._extract_root_from_chain(chain)
            
            all_underlying.extend(underlying)
            all_root.append(root)
        
        rca_data["five_why_chains"] = all_chains
        rca_data["underlying_causes"] = all_underlying
        rca_data["root_causes"] = all_root
        
        # ADIM 3: Rapor oluştur
        try:
            rca_data["final_report_tr"] = self._generate_final_report(rca_data)
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {e}")
            rca_data["final_report_tr"] = "Rapor oluşturulamadı."
        
        print("\n✅ Kök neden analizi tamamlandı!")
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
    
    def _identify_immediate_causes(self, incident_summary: str) -> List[Dict]:
        """
        ADIM 1: Doğrudan nedenleri belirle (A/B kategorileri)
        """
        
        # Bilgi tabanından A ve B kategorilerini al
        category_a = get_category_text('A')
        category_b = get_category_text('B')
        
        prompt = f"""Sen bir İSG kaza araştırma uzmanısın. HSG245 metodolojisini kullanıyorsun.

OLAY ÖZETİ:
{incident_summary}

REFERANS KATEGORİLERİ:
{category_a}

{category_b}

GÖREV:
1. Bu olayın DOĞRUDAN NEDENLERİNİ (Immediate Causes) belirle
2. Yukarıdaki A ve B kategorilerinden en uygun olanları kullan (ama KOD YAZMA!)
3. Tipik olarak 2-4 doğrudan neden olur
4. Her neden için DETAYLI AÇIKLAMA yaz (ne oldu + neden önemli)

CRITICAL RULES:
- KOD YAZMA! Sadece açıklama yaz
  ✅ Doğru: "Operatör makineye yetkisiz müdahale etti ve koruyucu kapağı kaldırdı"
  ❌ Yanlış: "A2.1 Ekipman yanlış kullanım"
- Her "cause" alanı en az 2 cümle olmalı
- "evidence" alanında somut kanıtlar belirt

Return JSON with:
{{
  "causes": [
    {{
      "cause": "Detaylı açıklama (KOD YOK)",
      "cause_tr": "Detaylı açıklama (KOD YOK)",
      "evidence": "Somut kanıtlar",
      "evidence_tr": "Somut kanıtlar"
    }}
  ]
}}

CRITICAL: All fields must be 100% in TURKISH. NO CATEGORY CODES in text!

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are an HSG245 expert. Return only valid JSON with ALL content in TURKISH."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            data = json.loads(result)
            causes = data.get("causes", [])
            
            # Kod temizleme
            import re
            code_pattern = r'\b[ABCD]\d+(\.\d+)?\b'
            
            for item in causes:
                # cause alanından kod temizle
                if item.get("cause"):
                    original = item["cause"]
                    cleaned = re.sub(code_pattern, '', item["cause"]).strip()
                    cleaned = re.sub(r'^[\s\-:]+', '', cleaned).strip()
                    item["cause"] = cleaned
                    
                    if original != cleaned:
                        print(f"      🧹 Kod temizlendi")
                
                # cause_tr de temizle
                if item.get("cause_tr"):
                    cleaned_tr = re.sub(code_pattern, '', item["cause_tr"]).strip()
                    cleaned_tr = re.sub(r'^[\s\-:]+', '', cleaned_tr).strip()
                    item["cause_tr"] = cleaned_tr
            
            # Türkçe alanları ana alanlara kopyala
            for item in causes:
                if item.get("cause_tr"):
                    item["cause"] = item["cause_tr"]
                if item.get("evidence_tr"):
                    item["evidence"] = item["evidence_tr"]
            
            print(f"   ✅ {len(causes)} doğrudan neden belirlendi")
            return causes
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse hatası: {e}")
            return []
    
    def _perform_5why_for_cause(self, immediate_cause: Dict, incident_summary: str) -> Dict:
        """
        ADIM 2: 5 Why analizi (C/D kategorileri)
        """
        cause_text = immediate_cause.get("cause", "")
        
        # C ve D kategorilerini al
        category_c = get_category_text('C')
        category_d = get_category_text('D')
        
        prompt = f"""Sen 5-Why analizi yapan bir İSG uzmanısın. HSG245 kullanıyorsun.

OLAY: {incident_summary}
DOĞRUDAN NEDEN: {cause_text}

KÖK NEDEN KATEGORİLERİ:
{category_c}

{category_d}

GÖREV: 5 Neden Analizi - KRONOLOJİK SIRA ÇOK ÖNEMLİ!

CRITICAL RULE - SIRALAMA:
Why 1 (Level 1) → Why 2 (Level 2) → Why 3 (Level 3) → Why 4 (Level 4) → Why 5 (Level 5 - ROOT)

❌ YANLIŞ: 1→3→5→2
✅ DOĞRU: 1→2→3→4→5

Her "why" bir önceki "because" cevabının nedenidir. Merdiven gibi: 1→2→3→4→5

Return JSON:
{{
  "immediate_cause": {{{{"cause": "{cause_text}", "cause_tr": "{cause_text"}}}},
  "why_chain": [
    {{"level": 1, "cause_type": "immediate", "why_question": "Neden?", "why_question_tr": "Neden?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 2, "cause_type": "underlying", "why_question": "Neden [Level 1]?", "why_question_tr": "Neden [Level 1]?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 3, "cause_type": "underlying", "why_question": "Neden [Level 2]?", "why_question_tr": "Neden [Level 2]?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 4, "cause_type": "underlying", "why_question": "Neden [Level 3]?", "why_question_tr": "Neden [Level 3]?", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 5, "cause_type": "root", "why_question": "Neden [Level 4]?", "why_question_tr": "Neden [Level 4]?", "because_answer": "... (C veya D kategorisinden)", "because_answer_tr": "... (C veya D kategorisinden)"}}
  ],
  "root_cause": {{"root": "Level 5 cevabı", "root_tr": "Level 5 cevabı"}}
}}

IMPORTANT:
- Level 5 ROOT CAUSE yukarıdaki C/D kategorilerinden biri olmalı
- All _tr fields: 100% TURKISH
- SIRALAMA: 1→2→3→4→5 (asla atlama!)

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are a 5 Why expert. Return only JSON with all _tr in TURKISH."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            chain = json.loads(result)
            
            # Sıralama kontrolü
            why_chain = chain.get("why_chain", [])
            if why_chain:
                expected_levels = [1, 2, 3, 4, 5]
                actual_levels = [step.get("level", 0) for step in why_chain]
                
                if actual_levels != expected_levels:
                    print(f"      ⚠️ Sıralama hatası tespit edildi - Düzeltiliyor...")
                    for i, step in enumerate(why_chain, 1):
                        step["level"] = i
                        if i == 1:
                            step["cause_type"] = "immediate"
                        elif i == 5:
                            step["cause_type"] = "root"
                        else:
                            step["cause_type"] = "underlying"
                    print(f"      ✅ Düzeltildi: 1→2→3→4→5")
            
            # Türkçeleştirme
            for step in why_chain:
                if step.get("why_question_tr"):
                    step["why_question"] = step["why_question_tr"]
                if step.get("because_answer_tr"):
                    step["because_answer"] = step["because_answer_tr"]
            
            # Root cause Türkçeleştir
            root = chain.get("root_cause", {})
            if isinstance(root, dict) and root.get("root_tr"):
                root["root"] = root["root_tr"]
                print(f"      ✓ Kök: {root.get('root', '')[:50]}...")
            
            return chain
        except json.JSONDecodeError as e:
            print(f"      ❌ JSON parse hatası: {e}")
            return {"immediate_cause": immediate_cause, "why_chain": [], "root_cause": {}}
    
    def _generate_final_report(self, rca_data: Dict) -> str:
        """Türkçe rapor oluştur"""
        print("\n📄 Final rapor hazırlanıyor...")
        
        raw_data_str = json.dumps(rca_data, indent=2, ensure_ascii=False)
        
        prompt = f"""Professional HSG245 Rapor Editörü olarak çalış.

INPUT (AI Analizi):
{raw_data_str}

GÖREV:
Bu veriden profesyonel 'Kök Neden Analiz Raporu' oluştur.

YAPISI:
- YÖNETİCİ ÖZETİ
- OLAY DETAYLARI
- DOĞRUDAN NEDENLER (Tüm immediate causes)
- KÖK NEDEN ANALİZİ (Her doğrudan neden için 5 Why zinciri detaylı açıkla)
- TEMEL NEDENLER (Level 2-4)
- SİSTEMİK BULGULAR (Level 5 root causes)
- SONUÇ VE ÖNERİLER

KURALLAR:
- SADECE TÜRKÇE (İngilizce kelime yok!)
- Formal, objektif, üst düzey İSG uzmanı üslubu
- Düzenli, temiz metin (JSON değil)

Return: Türkçe rapor metni (SADECE TÜRKÇE!)"""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a senior HSG245 expert in Turkey. You write ALL reports in TURKISH. Never use English."},
                {"role": "user", "content": prompt}
            ]
        )
        
        report = response.choices[0].message.content
        print("\n" + "="*80)
        print(report[:500] + "...")
        print("="*80)
        
        return report
    
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
