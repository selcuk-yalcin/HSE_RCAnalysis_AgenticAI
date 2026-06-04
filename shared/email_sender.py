"""
SMTP email sender for report delivery (P0.10). No-op when SMTP is not configured.
"""

from __future__ import annotations

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Tuple

AttachmentTuple = Tuple[str, bytes, str]  # filename, payload, mime_type


def _clean_env(value: str) -> str:
    """Strip whitespace and optional surrounding quotes from env vars."""
    v = (value or "").strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        v = v[1:-1].strip()
    return v


def smtp_configured() -> bool:
    host = (os.getenv("SMTP_HOST") or "").strip()
    return bool(host)


def get_smtp_public_config() -> dict[str, str | bool]:
    """Non-secret SMTP summary for ops UI / dashboard."""
    from_addr = _clean_env(os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or "noreply@inferaworld.com")
    return {
        "configured": smtp_configured(),
        "from_address": from_addr,
        "host": (os.getenv("SMTP_HOST") or "").strip(),
        "port": (os.getenv("SMTP_PORT") or "587").strip(),
        "use_tls": (os.getenv("SMTP_USE_TLS") or "1").strip().lower() not in ("0", "false", "no"),
    }


def send_email(
    to_address: str,
    subject: str,
    html_body: str,
    *,
    text_body: Optional[str] = None,
    attachments: Optional[List[AttachmentTuple]] = None,
) -> Tuple[bool, str, str]:
    """
    Returns (ok, provider_message_id, error_message).
    attachments: list of (filename, bytes, mime_type)
    """
    to_address = (to_address or "").strip()
    if not to_address:
        return False, "", "recipient_missing"
    if not smtp_configured():
        return False, "", "smtp_not_configured"

    host = os.getenv("SMTP_HOST", "").strip()
    port = int((os.getenv("SMTP_PORT") or "587").strip() or "587")
    user = _clean_env(os.getenv("SMTP_USER") or "")
    password = _clean_env(os.getenv("SMTP_PASSWORD") or "")
    from_addr = _clean_env(os.getenv("SMTP_FROM") or user or "noreply@inferaworld.com")
    use_tls = (os.getenv("SMTP_USE_TLS") or "1").strip().lower() not in ("0", "false", "no")

    plain = text_body or html_body
    att_list = attachments or []

    if att_list:
        msg = MIMEMultipart("mixed")
        alt = MIMEMultipart("alternative")
        alt.attach(MIMEText(plain, "plain", "utf-8"))
        alt.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(alt)
        for filename, payload, mime_type in att_list:
            main, sub = (mime_type.split("/", 1) + ["octet-stream"])[:2]
            part = MIMEBase(main, sub)
            part.set_payload(payload)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(part)
    else:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_address

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
