"""
Test script for Hierarchical Root Cause Analysis V2
"""

from agents.rootcause_agent_v2 import RootCauseAgentV2
import json

# Sample incident data
part1_data = {
    "brief_details": {
        "what": "Operatörün eli pres makinesinde sıkıştı ve ezildi",
        "where": "Üretim hattı, pres istasyonu",
        "when": "Gece vardiyası"
    }
}

part2_data = {
    "type_of_event": "Mekanik yaralanma - el ezilmesi",
    "actual_potential_harm": "Ciddi yaralanma",
    "investigation_level": "Detaylı inceleme gerekli"
}

investigation_data = {
    "how_happened": """Operatör gece vardiyasında pres makinesinde çalışıyordu. 
    Güvenlik switch'i (interlock) arızalı olduğu için üretim durmasın diye kısa devre yapılmıştı. 
    Operatör makineye yetkisi olmadığı halde müdahale etti ve eli koruyucu kapak açıkken sıkıştı. 
    Bakımcı gece vardiyasında yoktu ve yedek parça stokta bulunmuyordu."""
}

def main():
    print("🚀 Hiyerarşik Kök Neden Analizi V2 Test Ediliyor...")
    print("=" * 80)
    
    # Initialize agent
    agent = RootCauseAgentV2()
    
    # Perform analysis
    result = agent.analyze_root_causes(
        part1_data=part1_data,
        part2_data=part2_data,
        investigation_data=investigation_data
    )
    
    # Print results
    print("\n" + "=" * 80)
    print("📊 ANALİZ SONUÇLARI")
    print("=" * 80)
    
    print(f"\nToplam Dal Sayısı: {len(result['analysis_branches'])}")
    print(f"Toplam Kök Neden: {len(result['final_root_causes'])}")
    
    print("\n" + "=" * 80)
    print("📄 FİNAL RAPOR")
    print("=" * 80)
    print(result.get("final_report_tr", "Rapor oluşturulamadı"))
    
    # Save to file
    with open("test_hierarchical_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Sonuçlar 'test_hierarchical_output.json' dosyasına kaydedildi")

if __name__ == "__main__":
    main()
