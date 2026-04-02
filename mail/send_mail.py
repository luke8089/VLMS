"""
send_mail.py — Standalone email sender for MindStack LMS.

Usage (same interface as the old send_mail.php):
  echo '{"to_email":"a@b.com","to_name":"Alice","subject":"Hi","html_body":"<b>Hello</b>"}' | python send_mail.py

Reads a JSON payload from stdin, sends the email via SMTP, and prints a
JSON result to stdout:
  {"success": true}
  {"success": false, "error": "..."}
"""

import json
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
try:
    from config import MAIL_CONFIG
except ImportError:
    print(json.dumps({"success": False, "error": "Missing config.py"}))
    sys.exit(1)


def _out(payload: dict, code: int = 0) -> None:
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(code)


# ---------------------------------------------------------------------------
# Read + validate stdin payload
# ---------------------------------------------------------------------------
raw = sys.stdin.read()
if not raw or not raw.strip():
    _out({"success": False, "error": "Empty input"}, 1)

try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    _out({"success": False, "error": f"Invalid JSON payload: {exc}"}, 1)

if not isinstance(data, dict):
    _out({"success": False, "error": "Payload must be a JSON object"}, 1)

to_email = str(data.get("to_email", "")).strip()
to_name  = str(data.get("to_name",  "User")).strip() or "User"
subject  = str(data.get("subject",  "No Subject")).strip()
html_body = str(data.get("html_body", ""))
text_body = str(data.get("text_body", "")) or html_body  # fallback

if not to_email:
    _out({"success": False, "error": "Missing recipient email"}, 1)

# ---------------------------------------------------------------------------
# Validate config
# ---------------------------------------------------------------------------
smtp_cfg = MAIL_CONFIG.get("smtp", {})
from_cfg = MAIL_CONFIG.get("from", {})

smtp_host = str(smtp_cfg.get("host", "")).strip()
smtp_user = str(smtp_cfg.get("username", "")).strip()
smtp_pass = str(smtp_cfg.get("password", "")).strip()
smtp_port = int(smtp_cfg.get("port", 587))
encryption = str(smtp_cfg.get("encryption", "tls")).lower()

from_email = str(from_cfg.get("email", smtp_user)).strip()
from_name  = str(from_cfg.get("name",  "MindStack LMS")).strip()

if not smtp_host or not smtp_user:
    _out({"success": False, "error": "Invalid SMTP configuration"}, 1)

# ---------------------------------------------------------------------------
# Build message
# ---------------------------------------------------------------------------
msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"]    = f"{from_name} <{from_email}>"
msg["To"]      = f"{to_name} <{to_email}>"

msg.attach(MIMEText(text_body, "plain", "utf-8"))
if html_body:
    msg.attach(MIMEText(html_body, "html", "utf-8"))

# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------
try:
    if encryption == "ssl":
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to_email], msg.as_bytes())
    else:
        # STARTTLS (default for port 587)
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to_email], msg.as_bytes())

    _out({"success": True})

except smtplib.SMTPAuthenticationError:
    _out({"success": False, "error": "SMTP authentication failed — check username/password"}, 1)
except smtplib.SMTPException as exc:
    _out({"success": False, "error": f"SMTP error: {exc}"}, 1)
except Exception as exc:
    _out({"success": False, "error": str(exc)}, 1)
