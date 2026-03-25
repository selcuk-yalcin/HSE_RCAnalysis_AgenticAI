"""
5-Why Decision Tree Generator - Exact Photo Format
Format: Initial Event → Why-1 → Why-2 → Why-3 → Why-4 → Why-5 → Root Cause
3 parallel branches with arrows showing the flow exactly as in the photo
"""
from typing import Dict, List


class DecisionTreeGeneratorPhoto:
    """Fotoğraftaki tam formatta decision tree oluşturur."""
    
    def generate_mermaid(self, rca_data: Dict, output_path: str = None) -> str:
        """RCA verilerinden Mermaid flowchart oluşturur - tam foto formatı."""
        
        incident_event = rca_data.get("incident_event", "")
        branches = rca_data.get("analysis_branches", [])
        
        # Başlık ve açıklama
        mermaid_code = """graph LR
    Start["<b>OLAY</b><br/>Forklift kapıya çarptı"]
    
    Note["<b>Nasıl Olunur:</b> Her dal OLAYDAN başlar → WHY-1 sorusu sorar → Zincirleme derileşme WHY 2, 3, 4 → KÖK NEDEN bulunur"]
    Note -.->|açıklama| Start
    
"""
        
        # Her dal için mermaid nodu oluştur
        branch_connections = []
        
        for branch_idx, branch in enumerate(branches, 1):
            branch_title = branch.get("branch_title", f"Branch {branch_idx}")
            questions_and_answers = branch.get("questions_and_answers", [])
            root_cause = branch.get("root_cause", {})
            
            if not questions_and_answers:
                continue
            
            # Branch ID
            bid = f"B{branch_idx}"
            
            # Branch başlığı
            mermaid_code += f'    {bid}_Title["<b>{branch_title}</b>"]\n'
            mermaid_code += f'    Start --> {bid}_Title\n\n'
            
            # Her why için node oluştur
            prev_node = f"{bid}_Title"
            
            for qa_idx, qa in enumerate(questions_and_answers, 1):
                question = qa.get("question", "")
                answer = qa.get("answer", "")
                
                # Soru nodu
                q_node = f"{bid}_Q{qa_idx}"
                mermaid_code += f'    {q_node}["<b>WHY-{qa_idx}</b><br/>{question}"]\n'
                mermaid_code += f'    {prev_node} --> {q_node}\n'
                
                # Cevap nodu
                a_node = f"{bid}_A{qa_idx}"
                # Cevabı kısalt (uzun cevaplar için)
                answer_short = answer[:80] + "..." if len(answer) > 80 else answer
                mermaid_code += f'    {a_node}["<b>CEVAP-{qa_idx}</b><br/>{answer_short}"]\n'
                mermaid_code += f'    {q_node} --> {a_node}\n'
                
                prev_node = a_node
            
            # Kök neden nodu
            if root_cause:
                code = root_cause.get("code", "")
                title = root_cause.get("title", "")
                
                rc_node = f"{bid}_RC"
                mermaid_code += f'    {rc_node}["<b>KÖK NEDEN ({code})</b><br/>{title}"]\n'
                mermaid_code += f'    {prev_node} --> {rc_node}\n'
                mermaid_code += f'    style {rc_node} fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000\n'
            
            mermaid_code += "\n"
        
        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5-Why Decision Tree</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 20px;
            background: white;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>5-WHY ANALİZİ - DECISION TREE</h1>
    <div class="subtitle">Forklift Sarmal Kapı Çarpışması - 21.03.2026</div>
    
    <div class="mermaid">
{mermaid_code}
    </div>
    
    <script>
        mermaid.contentLoaded();
    </script>
</body>
</html>"""
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
