"""
5-Why Decision Tree Generator v2
==================================
Adım adım, detaylı 5-Why analizi gösterir.
- Olay tam açıklaması
- Her dal için ayrı kutu
- Neden 1 → Cevap 1 → Neden 2 → Cevap 2 şeklinde gösterir
- Renkli kutuyla sonuçta kök neden
"""

from typing import Dict, List, Optional, Any
from pathlib import Path


class DecisionTreeGeneratorV2:
    """5-Why analizinden detaylı HTML oluşturur."""
    
    def __init__(self):
        pass
        
    def generate_html(
        self, 
        rca_data: Dict[str, Any],
        output_path: Optional[str] = None,
        incident_title: str = "Kaza Analizi"
    ) -> str:
        """
        RCA verilerinden detaylı decision tree HTML oluşturur.
        
        Args:
            rca_data: Kök neden analizi verileri
            output_path: HTML dosyası kaydedilecek yer (opsiyonel)
            incident_title: Olayın başlığı
            
        Returns:
            HTML string
        """
        # Dalları bul
        branches = rca_data.get("analysis_branches", rca_data.get("branches", []))
        
        # Olay açıklaması
        incident_event = rca_data.get("incident_event", incident_title)
        if isinstance(incident_event, dict):
            incident_event = incident_event.get("title", incident_title)
        
        # HTML oluştur
        html = self._generate_html_template(branches, incident_event, incident_title)
        
        # Dosyaya kaydet
        if output_path:
            Path(output_path).write_text(html, encoding='utf-8')
        
        return html
    
    def _generate_html_template(self, branches: List[Dict], incident_event: str, incident_title: str) -> str:
        """HTML template'ini oluşturur."""
        
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
            font-family: 'Arial', sans-serif;
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
            border-radius: 3px;
            padding: 8px;
            margin-bottom: 8px;
        }}
        
        .why-label {{
            font-weight: bold;
            color: #ff9800;
            font-size: 11px;
            margin-bottom: 3px;
            display: inline-block;
            background: #fff3e0;
            padding: 2px 6px;
            border-radius: 2px;
        }}
        
        .why-question {{
            font-weight: bold;
            color: #000;
            font-size: 11px;
            margin-bottom: 4px;
            margin-top: 3px;
        }}
        
        .why-answer {{
            color: #333;
            font-size: 10px;
            line-height: 1.5;
            margin-left: 8px;
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
            font-size: 10px;
            margin-bottom: 4px;
            display: inline-block;
        }}
        
        .root-cause .code {{
            font-size: 10px;
            color: #666;
            margin-bottom: 3px;
            font-weight: bold;
        }}
        
        .root-cause .title {{
            font-weight: bold;
            color: #c62828;
            font-size: 11px;
            margin-bottom: 3px;
        }}
        
        .root-cause .content {{
            font-size: 10px;
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
            OLAY: {incident_event}
        </div>
        
        {branches_html}
    </div>
</body>
</html>"""
    
    def _generate_branch_html(self, branch: Dict, branch_idx: int) -> str:
        """Bir dalın HTML'ini oluşturur."""
        
        branch_title = branch.get("branch_title", f"Dal {branch_idx}")
        why_chain = branch.get("questions_and_answers", branch.get("why_chain", []))
        root_cause = branch.get("root_cause", {})
        
        # Why items HTML
        why_items_html = ""
        for why_idx, why_item in enumerate(why_chain, 1):
            question = why_item.get("question", "")
            answer = why_item.get("answer", "")
            
            why_items_html += f"""
        <div class="why-item">
            <div class="why-label">NEDEN {why_idx}</div>
            <div class="why-question">{question}</div>
            <div class="why-answer">→ {answer}</div>
        </div>"""
        
        # Kök neden HTML
        root_code = root_cause.get("code", "")
        root_title = root_cause.get("title", "Kök Neden")
        root_cause_text = root_cause.get("cause_tr", root_cause.get("cause", ""))
        
        root_html = f"""
        <div class="root-cause">
            <div class="label">KÖK NEDEN</div>
            <div class="code">Kod: {root_code}</div>
            <div class="title">{root_title}</div>
            <div class="content">{root_cause_text}</div>
        </div>"""
        
        return f"""
    <div class="branch">
        <div class="branch-title">{branch_idx}. {branch_title}</div>
        {why_items_html}
        {root_html}
    </div>"""


def generate_decision_tree_html_v2(
    rca_data: Dict[str, Any],
    output_path: str,
    incident_title: str = "Kaza Analizi"
) -> str:
    """Kolaylık fonksiyonu."""
    generator = DecisionTreeGeneratorV2()
    return generator.generate_html(rca_data, output_path, incident_title)
