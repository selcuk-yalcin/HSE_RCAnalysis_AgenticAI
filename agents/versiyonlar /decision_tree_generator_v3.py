"""
5-Why Decision Tree Generator V3
Format: Fotoğraf gibi - Olay özeti → İlk soru → Cevaplar → Neden 2-5 → Kök neden
"""
from typing import Dict, List


class DecisionTreeGeneratorV3:
    """Fotoğrafta görünen formatta decision tree oluşturur."""
    
    def generate_html(self, rca_data: Dict, output_path: str = None, incident_title: str = "") -> str:
        """RCA verilerinden HTML decision tree oluşturur."""
        
        incident_event = rca_data.get("incident_event", "")
        branches = rca_data.get("analysis_branches", [])
        
        html = self._generate_html_template(branches, incident_event, incident_title)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
    
    def _generate_html_template(self, branches: List[Dict], incident_event: str, incident_title: str) -> str:
        """Fotoğraf formatında HTML template oluşturur."""
        
        # Her dal için HTML oluştur
        branches_html = ""
        for branch_idx, branch in enumerate(branches, 1):
            branches_html += self._generate_branch_html(branch, branch_idx)
        
        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5-Why Analizi - {incident_title}</title>
    <style>
        @page {{
            size: A4 landscape;
            margin: 8mm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            background: white;
            padding: 8mm;
            line-height: 1.4;
        }}
        
        .container {{
            max-width: 100%;
            background: white;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 10px;
            border-bottom: 2px solid #333;
            padding-bottom: 8px;
        }}
        
        .header h1 {{
            font-size: 16px;
            margin-bottom: 2px;
            color: #000;
            font-weight: bold;
        }}
        
        .header .subtitle {{
            font-size: 10px;
            color: #666;
            margin-bottom: 3px;
        }}
        
        .event-summary {{
            background: #f5f5f5;
            border: 1px solid #999;
            border-radius: 3px;
            padding: 8px;
            margin-bottom: 10px;
            font-size: 11px;
            font-weight: bold;
            color: #000;
            text-align: center;
        }}
        
        .branch {{
            page-break-inside: avoid;
            margin-bottom: 12px;
            background: white;
        }}
        
        .branch-title {{
            background: #333;
            color: white;
            padding: 6px 10px;
            font-weight: bold;
            font-size: 11px;
            margin-bottom: 8px;
            border-radius: 3px;
        }}
        
        .why-block {{
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-left: 3px solid #ff9800;
            border-radius: 2px;
            padding: 8px;
            margin-bottom: 6px;
        }}
        
        .why-label {{
            font-weight: bold;
            color: #ff9800;
            font-size: 10px;
            margin-bottom: 3px;
            display: inline-block;
            background: #fff3e0;
            padding: 2px 6px;
            border-radius: 2px;
        }}
        
        .why-question {{
            font-weight: bold;
            color: #000;
            font-size: 10px;
            margin-bottom: 4px;
            margin-top: 3px;
            line-height: 1.4;
        }}
        
        .why-answer {{
            color: #333;
            font-size: 9px;
            line-height: 1.5;
            margin-left: 0px;
            padding: 6px;
            background: white;
            border-left: 2px solid #ff9800;
            padding-left: 10px;
            border-radius: 2px;
        }}
        
        .root-cause {{
            background: #ffebee;
            border: 2px solid #c62828;
            border-radius: 3px;
            padding: 8px;
            margin-top: 8px;
        }}
        
        .root-cause .label {{
            background: #c62828;
            color: white;
            padding: 4px 8px;
            border-radius: 2px;
            font-weight: bold;
            font-size: 9px;
            margin-bottom: 4px;
            display: inline-block;
        }}
        
        .root-cause .code {{
            font-size: 9px;
            color: #666;
            margin-bottom: 3px;
            font-weight: bold;
        }}
        
        .root-cause .title {{
            font-weight: bold;
            color: #c62828;
            font-size: 10px;
            margin-bottom: 3px;
        }}
        
        .root-cause .content {{
            font-size: 9px;
            color: #333;
            line-height: 1.5;
            padding: 6px;
            background: white;
            border-radius: 2px;
            border-left: 2px solid #c62828;
            padding-left: 8px;
        }}
        
        @media print {{
            body {{
                padding: 8mm;
            }}
            .branch {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>5-WHY ANALİZİ AĞACI (DECISION TREE)</h1>
            <div class="subtitle">{incident_title} - Kök Neden Analizi</div>
        </div>
        
        <div class="event-summary">
            OLAY ÖZETİ: {incident_event}
        </div>
        
        {branches_html}
    </div>
</body>
</html>"""
    
    def _generate_branch_html(self, branch: Dict, branch_idx: int) -> str:
        """Fotoğrafta görünen format: Olay → İlk soru kutusu → Cevaplar zincirleme."""
        
        branch_title = branch.get("branch_title", f"Branch {branch_idx}")
        questions_and_answers = branch.get("questions_and_answers", [])
        root_cause = branch.get("root_cause", {})
        
        if not questions_and_answers:
            return ""
        
        # İLK SORU - ayrı kutuda en başta
        first_qa = questions_and_answers[0]
        first_question = first_qa.get("question", "")
        first_answer = first_qa.get("answer", "")
        
        why_chain_html = f"""
    <div class="branch">
        <div class="branch-title">{branch_title}</div>
        
        <div class="why-block">
            <div class="why-label">❓ İLK SORU</div>
            <div class="why-question">{first_question}</div>
        </div>
        
        <div class="why-block">
            <div class="why-label">💡 CEVAP</div>
            <div class="why-answer">{first_answer}</div>
        </div>
        """
        
        # NEDEN 2-5 sorular ve cevaplar
        for i, qa in enumerate(questions_and_answers[1:], start=2):
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            
            why_chain_html += f"""
        <div class="why-block">
            <div class="why-label">❓ NEDEN {i}</div>
            <div class="why-question">{question}</div>
        </div>
        
        <div class="why-block">
            <div class="why-label">💡 CEVAP {i}</div>
            <div class="why-answer">{answer}</div>
        </div>
        """
        
        # Kök neden kutusu
        if root_cause:
            code = root_cause.get("code", "")
            title = root_cause.get("title", "")
            cause_tr = root_cause.get("cause_tr", "")
            
            why_chain_html += f"""
        <div class="root-cause">
            <div class="label">🎯 KÖK NEDEN</div>
            <div class="code">Kod: {code}</div>
            <div class="title">{title}</div>
            <div class="content">{cause_tr}</div>
        </div>
        """
        
        why_chain_html += f"""
    </div>
    """
        
        return why_chain_html
