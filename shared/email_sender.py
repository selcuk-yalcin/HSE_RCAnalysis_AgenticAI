"""
SMTP email sender for report delivery (P0.10). No-op when SMTP is not configured.
"""

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Tuple


def smtp_configured() -> bool:
    host = (os.getenv("SMTP_HOST") or "").strip()
    return bool(host)


def send_email(
    to_address: str,
    subject: str,
    html_body: str,
    *,
    text_body: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """
    Returns (ok, provider_message_id, error_message).
    """
    to_address = (to_address or "").strip()
    if not to_address:
        return False, "", "recipient_missing"
    if not smtp_configured():
        return False, "", "smtp_not_configured"

    host = os.getenv("SMTP_HOST", "").strip()
    port = int((os.getenv("SMTP_PORT") or "587").strip() or "587")
    user = (os.getenv("SMTP_USER") or "").strip()
    password = (os.getenv("SMTP_PASSWORD") or "").strip()
    from_addr = (os.getenv("SMTP_FROM") or user or "noreply@inferaworld.com").strip()
    use_tls = (os.getenv("SMTP_USE_TLS") or "1").strip().lower() not in ("0", "false", "no")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_address
    plain = text_body or html_body
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            if use_tls:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(from_addr, [to_address], msg.as_string())
        msg_id = f"smtp-{hash((to_address, subject)) & 0xFFFFFFFF:08x}"
        return True, msg_id, ""
    except Exception as exc:  # noqa: BLE001
        return False, "", str(exc)
