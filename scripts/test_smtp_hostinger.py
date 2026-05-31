#!/usr/bin/env python3
"""
Hostinger SMTP connectivity + test mail (P0.10 ops).

Usage:
  export SMTP_HOST=smtp.hostinger.com
  export SMTP_PORT=587
  export SMTP_USE_TLS=1
  export SMTP_USER=info@inferaworld.com
  export SMTP_PASSWORD='your-mailbox-password'
  export SMTP_FROM='Infera Raporlar <info@inferaworld.com>'
  python scripts/test_smtp_hostinger.py --to yalcinselcuk0@gmail.com

Dry-run (no send):
  python scripts/test_smtp_hostinger.py --check-only
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _load_dotenv_file(path: str) -> None:
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


_load_dotenv_file(os.path.join(ROOT, ".env.smtp"))
_load_dotenv_file(os.path.join(ROOT, ".env"))

from shared.email_sender import get_smtp_public_config, send_email, smtp_configured  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Hostinger SMTP for Infera report delivery")
    parser.add_argument("--to", help="Test recipient email (defaults to SMTP_USER)")
    parser.add_argument("--check-only", action="store_true", help="Only print config, do not send")
    args = parser.parse_args()

    cfg = get_smtp_public_config()
    print("=== SMTP config (non-secret) ===")
    for k, v in cfg.items():
        print(f"  {k}: {v}")

    if not smtp_configured():
        print("\nERROR: SMTP_HOST is not set.")
        return 1

    if not (os.getenv("SMTP_PASSWORD") or "").strip():
        print("\nERROR: SMTP_PASSWORD is not set.")
        return 1

    if args.check_only:
        print("\nOK: configuration looks ready (password present).")
        return 0

    to_addr = (args.to or os.getenv("SMTP_TEST_TO") or os.getenv("SMTP_USER") or "").strip()
    if not to_addr:
        print("\nERROR: pass --to or set SMTP_USER")
        return 1

    print(f"\nSending test mail to {to_addr} ... (Hostinger SMTP, ~5-30s)", flush=True)

    subject = "Infera SMTP test — rapor teslimatı hazır"
    body = """
    <p>Bu bir test e-postasıdır.</p>
    <p>Hostinger SMTP (<strong>info@inferaworld.com</strong>) yapılandırması çalışıyor.</p>
    <p>Rapor tamamlandığında benzer bir mail otomatik gidecek.</p>
    """
    ok, msg_id, err = send_email(to_addr, subject, body)
    if ok:
        print(f"\nOK: test mail sent to {to_addr} (id={msg_id})")
        return 0
    print(f"\nFAIL: {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
