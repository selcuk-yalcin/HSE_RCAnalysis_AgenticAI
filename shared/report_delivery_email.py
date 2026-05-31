"""
Localized report-ready notification email (P0.10).
"""

from __future__ import annotations

from typing import Dict, Tuple


def normalize_delivery_lang(code: str | None) -> str:
    raw = (code or "tr").strip().lower()
    if raw.startswith("en"):
        return "en"
    return "tr"


def build_report_ready_email(
    *,
    incident_id: str,
    output_language: str = "tr",
    docx_link: str = "",
) -> Tuple[str, str, str]:
    """
    Returns (subject, html_body, plain_body).
    HTML report is described as an attachment in the body (actual file attached separately).
    """
    lang = normalize_delivery_lang(output_language)
    ref = incident_id or "—"

    if lang == "en":
        subject = "Your root cause analysis report is ready"
        html_body = f"""
        <p>Hello,</p>
        <p>Your <strong>English</strong> root cause analysis report for incident
        <strong>{ref}</strong> has been created.</p>
        <p>The HTML report is <strong>attached</strong> to this email
        (<code>{ref}_report.html</code>).</p>
        """
        plain = (
            f"Hello,\n\nYour English root cause analysis report for incident {ref} "
            f"has been created.\nThe HTML report is attached ({ref}_report.html).\n"
        )
        if docx_link:
            html_body += f"""
            <p>You can also download the Word (DOCX) version here
            (link valid 24 hours):<br>
            <a href="{docx_link}">Download DOCX</a></p>
            """
            plain += f"\nDOCX download (24h): {docx_link}\n"
        html_body += "<p>This message was sent only to your account.</p>"
        plain += "\nThis message was sent only to your account."
        return subject, html_body.strip(), plain.strip()

    subject = "Kök neden analiz raporunuz hazır"
    html_body = f"""
    <p>Merhaba,</p>
    <p><strong>{ref}</strong> referanslı kök neden analiz raporunuz oluşturuldu.</p>
    <p>HTML rapor bu e-postaya <strong>ek</strong> olarak gönderilmiştir
    (<code>{ref}_report.html</code>).</p>
    """
    plain = (
        f"Merhaba,\n\n{ref} referanslı kök neden analiz raporunuz oluşturuldu.\n"
        f"HTML rapor eke eklenmiştir ({ref}_report.html).\n"
    )
    if docx_link:
        html_body += f"""
        <p>Word (DOCX) sürümünü buradan da indirebilirsiniz (24 saat geçerli):<br>
        <a href="{docx_link}">DOCX indir</a></p>
        """
        plain += f"\nDOCX indirme (24s): {docx_link}\n"
    html_body += "<p>Bu mesaj yalnızca hesabınıza gönderilmiştir.</p>"
    plain += "\nBu mesaj yalnızca hesabınıza gönderilmiştir."
    return subject, html_body.strip(), plain.strip()
