"""
Test V2 to Frontend transformation
"""

# Mock V2 output
v2_output = {
    "incident_summary": "Test incident",
    "analysis_branches": [
        {
            "branch_number": 1,
            "immediate_cause": {
                "code": "B1.6",
                "category_type": "MEKANİK/FİZİKSEL",
                "cause_tr": "Güvenlik switch'i baypas edilmişti",
                "evidence_tr": "Koruyucu cihaz devre dışı"
            },
            "why_chain": [
                {
                    "level": 1,
                    "question_tr": "Neden baypas edildi?",
                    "answer_tr": "Switch arızalıydı"
                },
                {
                    "level": 2,
                    "question_tr": "Neden değiştirilmedi?",
                    "answer_tr": "Yedek parça yoktu"
                }
            ],
            "root_cause": {
                "code": "D6.1",
                "category_type": "ORGANİZASYONEL",
                "cause_tr": "Yetersiz Bakım Stratejisi",
                "explanation_tr": "Bakım planlaması eksik"
            }
        },
        {
            "branch_number": 2,
            "immediate_cause": {
                "code": "A1.4",
                "category_type": "DAVRANIŞSAL",
                "cause_tr": "Operatör yetkisiz müdahale etti",
                "evidence_tr": "Güvenlik prosedürü ihlali"
            },
            "why_chain": [
                {
                    "level": 1,
                    "question_tr": "Neden müdahale etti?",
                    "answer_tr": "Üretim durmasın diye"
                }
            ],
            "root_cause": {
                "code": "D1.4",
                "category_type": "ORGANİZASYONEL",
                "cause_tr": "Yetersiz Eğitim",
                "explanation_tr": "Güvenlik eğitimi verilmemiş"
            }
        }
    ],
    "final_root_causes": [],
    "analysis_method": "HSG245 Hierarchical 5-Why",
    "final_report_tr": "Test rapor"
}

# Transform function
def transform_v2_to_frontend(part3_raw: dict) -> dict:
    immediate_causes = []
    underlying_causes = []
    root_causes = []
    
    for branch in part3_raw.get("analysis_branches", []):
        imm = branch.get("immediate_cause", {})
        if imm:
            immediate_causes.append({
                "code": imm.get("code", ""),
                "category": imm.get("category_type", ""),
                "description": imm.get("cause_tr", imm.get("cause", "")),
                "evidence": imm.get("evidence_tr", "")
            })
        
        why_chain = branch.get("why_chain", [])
        for why in why_chain:
            underlying_causes.append({
                "level": why.get("level", 0),
                "question": why.get("question_tr", ""),
                "answer": why.get("answer_tr", ""),
                "branch": branch.get("branch_number", 0)
            })
        
        root = branch.get("root_cause", {})
        if root:
            root_causes.append({
                "code": root.get("code", ""),
                "category": root.get("category_type", ""),
                "description": root.get("cause_tr", root.get("cause", "")),
                "explanation": root.get("explanation_tr", ""),
                "branch": branch.get("branch_number", 0)
            })
    
    return {
        "immediate_causes": immediate_causes,
        "underlying_causes": underlying_causes,
        "root_causes": root_causes,
        "analysis_method": part3_raw.get("analysis_method", "HSG245 Hierarchical 5-Why"),
        "incident_summary": part3_raw.get("incident_summary", ""),
        "final_report_tr": part3_raw.get("final_report_tr", ""),
        "_v2_raw": part3_raw
    }

# Test
result = transform_v2_to_frontend(v2_output)

print("="*80)
print("✅ TRANSFORMATION TEST")
print("="*80)

print(f"\n📌 Immediate Causes: {len(result['immediate_causes'])}")
for cause in result['immediate_causes']:
    print(f"   [{cause['code']}] {cause['description']}")

print(f"\n📊 Underlying Causes: {len(result['underlying_causes'])}")
for cause in result['underlying_causes']:
    print(f"   [Dal {cause['branch']} - Why {cause['level']}] {cause['question']}")
    print(f"      → {cause['answer']}")

print(f"\n🎯 Root Causes: {len(result['root_causes'])}")
for cause in result['root_causes']:
    print(f"   [{cause['code']}] {cause['description']}")
    print(f"      {cause['explanation']}")

print("\n" + "="*80)
print("✅ Frontend will receive proper format!")
print("="*80)
