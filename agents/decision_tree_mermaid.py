"""5-Why Decision Tree Generator — dikey (TD) tam sayfa okunabilir çıktı."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import re

try:
    from .report_text_sanitize import strip_hse_codes
except ImportError:
    from agents.report_text_sanitize import strip_hse_codes


class DecisionTreeGenerator:
    """5-Why analizinden decision tree HTML oluşturur."""

    def __init__(self):
        self.node_counter = 0
        self.question_nodes = {}
        self.answer_nodes = {}
        self.rendered_connections = set()

    def generate_html(self, rca_data: Dict[str, Any], output_path: Optional[str] = None, incident_title: str = "Kaza Analizi") -> str:
        branches = rca_data.get("branches", rca_data.get("analysis_branches", []))
        incident_event = rca_data.get("incident_event", incident_title)
        if isinstance(incident_event, dict):
            incident_event = incident_event.get("title", incident_title)

        if not branches:
            return self._generate_empty_html(incident_title)

        mermaid_code = self._generate_mermaid_graph(branches, incident_event)
        html = self._generate_html_template(mermaid_code, incident_title)

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(html, encoding='utf-8')

        return html

    def _generate_mermaid_graph(self, branches: List[Dict], incident_event: str) -> str:
        lines = ['graph TD']
        incident_event = strip_hse_codes(str(incident_event or ""))
        event_fmt = self._fmt(incident_event, 72)
        lines.append(f'    OLAY["<b>OLAY</b><br/>{event_fmt}"]')
        lines.append('    style OLAY fill:#fff,stroke:#333,stroke-width:2px,font-size:16px,font-weight:bold')
        lines.append('')

        self.node_counter = 0
        self.question_nodes = {}
        self.answer_nodes = {}
        self.rendered_connections = set()

        for branch_idx, branch in enumerate(branches, 1):
            why_chain = branch.get("why_chain", branch.get("questions_and_answers", []))
            prev_node = "OLAY"

            for why_idx, why_item in enumerate(why_chain, 1):
                question = strip_hse_codes(
                    str(why_item.get("question_tr", why_item.get("question", "")) or "")
                )
                answer = strip_hse_codes(
                    str(why_item.get("answer_tr", why_item.get("answer", "")) or "")
                )

                norm_q = self._norm(question)
                norm_qa = self._norm(f"{question}|||{answer}")

                if norm_q not in self.question_nodes:
                    self.node_counter += 1
                    q_node = f"Q{self.node_counter}"
                    self.question_nodes[norm_q] = q_node
                    q_fmt = self._fmt(question, 72)
                    label = f"<b>Neden {why_idx}:</b><br/>{q_fmt}"
                    lines.append(f'    {q_node}["{label}"]')
                    lines.append(f'    style {q_node} fill:#fff,stroke:#999,stroke-width:1px,stroke-dasharray:5 4,font-size:14px')
                else:
                    q_node = self.question_nodes[norm_q]

                self._add_conn(lines, prev_node, q_node)

                if norm_qa not in self.answer_nodes:
                    self.node_counter += 1
                    a_node = f"A{self.node_counter}"
                    self.answer_nodes[norm_qa] = a_node
                    a_fmt = self._fmt(answer, 72)
                    lines.append(f'    {a_node}["{a_fmt}"]')
                    lines.append(f'    style {a_node} fill:#fff,stroke:#666,stroke-width:1px,font-size:14px')
                else:
                    a_node = self.answer_nodes[norm_qa]

                self._add_conn(lines, q_node, a_node)
                prev_node = a_node

            root_cause = branch.get("root_cause", {})
            root_node = f"ROOT{branch_idx}"
            root_title = strip_hse_codes(str(root_cause.get("title", "Kök Neden") or ""))
            root_cause_text = strip_hse_codes(
                str(root_cause.get("cause_tr", root_cause.get("cause", "")) or "")
            )

            header = "<b>KÖK NEDEN</b>"
            title_fmt = self._fmt(root_title, 72)
            content = f"{header}<br/>{title_fmt}"
            if root_cause_text:
                cause_fmt = self._fmt(root_cause_text, 72)
                content += f"<br/>{cause_fmt}"

            lines.append(f'    {root_node}["{content}"]')
            lines.append(f'    style {root_node} fill:#e8e8e8,stroke:#000,stroke-width:2px,font-size:14px,font-weight:bold')
            self._add_conn(lines, prev_node, root_node)
            lines.append('')

        return '\n'.join(lines)

    def _add_conn(self, lines: list, src: str, dst: str) -> None:
        conn = f'    {src} --> {dst}'
        if conn not in self.rendered_connections:
            lines.append(conn)
            self.rendered_connections.add(conn)

    def _norm(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _fmt(self, text: str, max_line_length: int = 72) -> str:
        if not text:
            return ""
        text = text.strip()
        text = text.replace('"', "'").replace('\\', '/').replace('<', '&lt;').replace('>', '&gt;')
        words = text.split()
        lines_out, current, length = [], [], 0

        for word in words:
            if length + len(word) + 1 > max_line_length and current:
                lines_out.append(' '.join(current))
                current, length = [word], len(word)
            else:
                current.append(word)
                length += len(word) + 1

        if current:
            lines_out.append(' '.join(current))

        # Çok uzun düğümlerde tam cümle kaybını azalt (önceki: 12 satır kesiyordu)
        return '<br/>'.join(lines_out[:40])

    def _generate_html_template(self, mermaid_code: str, incident_title: str) -> str:
        safe_title = (
            str(incident_title or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5-WHY Decision Tree</title>
    <style>
        @page {{ size: A4 portrait; margin: 8mm; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{
            width: 100%;
            min-height: 100vh;
            font-family: 'Segoe UI', Arial, sans-serif;
            background: white;
        }}
        body {{
            display: flex;
            flex-direction: column;
            padding: 8px 12px;
            min-height: 100vh;
        }}
        header {{
            text-align: center;
            flex-shrink: 0;
            padding: 8px 0 12px;
        }}
        header .top-title {{ font-size: 13px; font-weight: bold; color: #333; margin-bottom: 4px; }}
        header h1 {{ font-size: 18px; font-weight: bold; color: #111; margin-bottom: 4px; }}
        header .subtitle {{ font-size: 13px; color: #444; max-width: 900px; margin: 0 auto; line-height: 1.4; }}
        .legend {{
            text-align: center;
            font-size: 12px;
            color: #444;
            padding: 8px 10px;
            background: #f5f5f5;
            border: 1px solid #ddd;
            flex-shrink: 0;
            margin-bottom: 8px;
        }}
        #diagram-wrap {{
            flex: 1;
            overflow: auto;
            width: 100%;
            min-height: calc(100vh - 140px);
            padding: 8px 4px 24px;
        }}
        #diagram-wrap .mermaid {{
            width: 100%;
            min-width: min(100%, 900px);
            margin: 0 auto;
        }}
        #diagram-wrap svg {{
            max-width: 100% !important;
            height: auto !important;
            display: block;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <header>
        <div class="top-title">5-WHY ANALİZ AĞACI (DECISION TREE)</div>
        <h1>5-WHY ANALİZ AĞACI</h1>
        <div class="subtitle">{safe_title}</div>
    </header>
    <div class="legend">Üstten alta: OLAY → NEDEN (kesik çerçeve) → CEVAP → KÖK NEDEN (koyu)</div>
    <div id="diagram-wrap">
        <div class="mermaid">
{mermaid_code}
        </div>
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                curve: 'basis',
                padding: 20,
                nodeSpacing: 28,
                rankSpacing: 56,
                useMaxWidth: false,
                htmlLabels: true,
                diagramPadding: 16
            }},
            themeVariables: {{
                fontSize: '14px',
                fontFamily: 'Segoe UI, Arial, sans-serif',
                primaryColor: '#fff',
                primaryTextColor: '#222',
                primaryBorderColor: '#333',
                lineColor: '#333',
                secondaryColor: '#f5f5f5',
                tertiaryColor: '#fff'
            }}
        }});
    </script>
</body>
</html>"""

    def _generate_empty_html(self, incident_title: str) -> str:
        return f"<html><body><h1>5-Why Analizi Bulunamadı</h1><p>Olay: {incident_title}</p></body></html>"


def generate_decision_tree_html(rca_data: Dict[str, Any], output_path: str, incident_title: str = "Kaza Analizi") -> str:
    generator = DecisionTreeGenerator()
    return generator.generate_html(rca_data, output_path, incident_title)
