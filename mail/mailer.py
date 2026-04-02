"""
mail/mailer.py — Email service for MindStack LMS.

Provides send_verification_email() and send_password_reset_email() called
directly from Flask routes. Uses stdlib smtplib — no PHP, no subprocess.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mail.config import MAIL_CONFIG  # mail/config.py — explicit package path


# ─────────────────────────── core sender ───────────────────────────

def send_email(to_email: str, to_name: str, subject: str,
               html_body: str, text_body: str = None) -> tuple:
    """
    Send an email via SMTP.
    Returns (True, '') on success, (False, error_message) on failure.
    """
    smtp_cfg  = MAIL_CONFIG.get('smtp', {})
    from_cfg  = MAIL_CONFIG.get('from', {})

    smtp_host  = str(smtp_cfg.get('host',     '')).strip()
    smtp_user  = str(smtp_cfg.get('username', '')).strip()
    smtp_pass  = str(smtp_cfg.get('password', '')).strip()
    smtp_port  = int(smtp_cfg.get('port', 587))
    encryption = str(smtp_cfg.get('encryption', 'tls')).lower()
    from_email = str(from_cfg.get('email', smtp_user)).strip()
    from_name  = str(from_cfg.get('name',  'MindStack LMS')).strip()

    if not smtp_host or not smtp_user:
        return False, 'SMTP is not configured in mail/config.py'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'{from_name} <{from_email}>'
    msg['To']      = f'{to_name} <{to_email}>'

    plain = text_body or _strip_tags(html_body)
    msg.attach(MIMEText(plain, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        if encryption == 'ssl':
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as srv:
                srv.login(smtp_user, smtp_pass)
                srv.sendmail(from_email, [to_email], msg.as_bytes())
        else:
            # STARTTLS — default for port 587
            with smtplib.SMTP(smtp_host, smtp_port) as srv:
                srv.ehlo()
                srv.starttls(context=ssl.create_default_context())
                srv.ehlo()
                srv.login(smtp_user, smtp_pass)
                srv.sendmail(from_email, [to_email], msg.as_bytes())

        return True, ''

    except smtplib.SMTPAuthenticationError:
        return False, 'SMTP authentication failed — check username / app password'
    except smtplib.SMTPException as exc:
        return False, f'SMTP error: {exc}'
    except Exception as exc:
        return False, str(exc)


# ─────────────────────────── verification email ───────────────────────────

def send_verification_email(first_name: str, to_email: str,
                            verify_url: str) -> tuple:
    """Send the account email-verification link to a newly registered user."""
    subject = 'Verify your MindStack account'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Verify your email — MindStack</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;min-height:100vh;">
    <tr><td align="center" style="padding:48px 16px;">

      <!-- Card -->
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#111111;border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px;overflow:hidden;max-width:520px;width:100%;">

        <!-- Header band -->
        <tr>
          <td style="background:#000000;padding:28px 40px;text-align:center;
                     border-bottom:1px solid rgba(255,255,255,0.06);">
            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr>
                <td style="width:36px;height:36px;background:#ffffff;border-radius:8px;
                           text-align:center;vertical-align:middle;padding:6px;">
                  <img src="https://img.icons8.com/ios-filled/36/000000/lightning-bolt.png"
                       width="22" height="22" alt="⚡" style="display:block;">
                </td>
                <td style="padding-left:10px;font-size:22px;font-weight:800;
                           color:#ffffff;letter-spacing:-0.5px;">MindStack</td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px 40px 32px;">
            <p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#ffffff;">
              Hi {first_name}, welcome! 👋
            </p>
            <p style="margin:0 0 24px;font-size:14px;color:rgba(255,255,255,0.5);line-height:1.6;">
              Thanks for creating a MindStack account. Please verify your email address
              to activate your account and get started.
            </p>

            <!-- CTA button -->
            <table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
              <tr>
                <td style="border-radius:10px;background:#ffffff;">
                  <a href="{verify_url}"
                     style="display:inline-block;padding:14px 32px;font-size:15px;
                            font-weight:700;color:#000000;text-decoration:none;
                            border-radius:10px;letter-spacing:-0.2px;">
                    Verify My Email
                  </a>
                </td>
              </tr>
            </table>

            <!-- Expiry note -->
            <p style="margin:0 0 24px;font-size:13px;color:rgba(255,255,255,0.35);line-height:1.5;">
              This link expires in <strong style="color:rgba(255,255,255,0.6);">24 hours</strong>.
              If you didn't create this account, you can safely ignore this email.
            </p>

            <!-- URL fallback -->
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                        border-radius:8px;padding:12px 16px;">
              <p style="margin:0 0 4px;font-size:11px;
                        color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.5px;">
                Or copy this link into your browser
              </p>
              <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.5);
                        word-break:break-all;font-family:monospace;">
                {verify_url}
              </p>
            </div>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:20px 40px 28px;border-top:1px solid rgba(255,255,255,0.06);">
            <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.2);text-align:center;">
              &copy; 2026 MindStack &nbsp;·&nbsp; Intelligent Learning, Stacked for You
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    text = (
        f"Hi {first_name},\n\n"
        f"Welcome to MindStack! Please verify your email address by visiting:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"If you did not create this account, ignore this email.\n\n"
        f"— MindStack Team"
    )

    return send_email(to_email, first_name, subject, html, text)


# ─────────────────────────── password reset email ───────────────────────────

def send_password_reset_email(first_name: str, to_email: str,
                              reset_url: str) -> tuple:
    """Send a password-reset link to the user."""
    subject = 'Reset your MindStack password'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Reset your password — MindStack</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;min-height:100vh;">
    <tr><td align="center" style="padding:48px 16px;">

      <!-- Card -->
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#111111;border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px;overflow:hidden;max-width:520px;width:100%;">

        <!-- Header band -->
        <tr>
          <td style="background:#000000;padding:28px 40px;text-align:center;
                     border-bottom:1px solid rgba(255,255,255,0.06);">
            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr>
                <td style="width:36px;height:36px;background:#ffffff;border-radius:8px;
                           text-align:center;vertical-align:middle;padding:6px;">
                  <img src="https://img.icons8.com/ios-filled/36/000000/lightning-bolt.png"
                       width="22" height="22" alt="⚡" style="display:block;">
                </td>
                <td style="padding-left:10px;font-size:22px;font-weight:800;
                           color:#ffffff;letter-spacing:-0.5px;">MindStack</td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px 40px 32px;">
            <p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#ffffff;">
              Reset your password
            </p>
            <p style="margin:0 0 8px;font-size:14px;color:rgba(255,255,255,0.5);line-height:1.6;">
              Hi {first_name}, we received a request to reset your MindStack password.
            </p>
            <p style="margin:0 0 24px;font-size:14px;color:rgba(255,255,255,0.5);line-height:1.6;">
              Click the button below to choose a new password. This link is valid for
              <strong style="color:rgba(255,255,255,0.6);">30 minutes</strong>.
            </p>

            <!-- CTA button -->
            <table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
              <tr>
                <td style="border-radius:10px;background:#ffffff;">
                  <a href="{reset_url}"
                     style="display:inline-block;padding:14px 32px;font-size:15px;
                            font-weight:700;color:#000000;text-decoration:none;
                            border-radius:10px;letter-spacing:-0.2px;">
                    Reset My Password
                  </a>
                </td>
              </tr>
            </table>

            <!-- Security note -->
            <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);
                        border-radius:8px;padding:12px 16px;margin-bottom:24px;">
              <p style="margin:0;font-size:13px;color:rgba(239,150,150,0.85);line-height:1.5;">
                If you did not request this, please ignore this email. Your password
                will not change until you click the link above and set a new one.
              </p>
            </div>

            <!-- URL fallback -->
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                        border-radius:8px;padding:12px 16px;">
              <p style="margin:0 0 4px;font-size:11px;
                        color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.5px;">
                Or copy this link into your browser
              </p>
              <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.5);
                        word-break:break-all;font-family:monospace;">
                {reset_url}
              </p>
            </div>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:20px 40px 28px;border-top:1px solid rgba(255,255,255,0.06);">
            <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.2);text-align:center;">
              &copy; 2026 MindStack &nbsp;·&nbsp; Intelligent Learning, Stacked for You
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    text = (
        f"Hi {first_name},\n\n"
        f"We received a request to reset your MindStack password.\n\n"
        f"Reset your password here:\n{reset_url}\n\n"
        f"This link expires in 30 minutes.\n\n"
        f"If you did not request this, ignore this email.\n\n"
        f"— MindStack Team"
    )

    return send_email(to_email, first_name, subject, html, text)


# ─────────────────────────── exam published notification ───────────────────────────

def send_exam_published_email(first_name: str, to_email: str,
                               exam_title: str, exam_type: str,
                               course_code: str, course_title: str,
                               lecturer_name: str,
                               start_time: str, end_time: str,
                               duration_minutes: int, total_marks: float,
                               dashboard_url: str) -> tuple:
    """Notify an enrolled student that a new exam / CAT has been published."""

    type_label_map = {
        'quiz':       'CAT / Quiz',
        'midterm':    'CAT 2 / Midterm',
        'final':      'Final / Main Exam',
        'assignment': 'Assignment',
    }
    type_label = type_label_map.get((exam_type or '').lower(), exam_type or 'Assessment')

    subject = f"New {type_label} posted — {course_code}: {exam_title}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;min-height:100vh;">
<tr><td align="center" style="padding:48px 16px;">

  <table width="520" cellpadding="0" cellspacing="0"
         style="background:#111111;border:1px solid rgba(255,255,255,0.08);
                border-radius:16px;overflow:hidden;max-width:520px;width:100%;">

    <!-- Header -->
    <tr><td style="background:#000000;padding:24px 36px;border-bottom:1px solid rgba(255,255,255,0.06);">
      <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
        <tr>
          <td style="width:32px;height:32px;background:#ffffff;border-radius:7px;
                     text-align:center;vertical-align:middle;">
            <span style="font-size:16px;line-height:32px;">⚡</span>
          </td>
          <td style="padding-left:10px;font-size:20px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">MindStack</td>
        </tr>
      </table>
    </td></tr>

    <!-- Colour band for assessment type -->
    <tr><td style="background:rgba(59,130,246,0.12);border-bottom:1px solid rgba(59,130,246,0.2);
                   padding:10px 36px;">
      <span style="font-size:11px;font-weight:700;color:#93c5fd;text-transform:uppercase;
                   letter-spacing:1px;">{type_label}</span>
    </td></tr>

    <!-- Body -->
    <tr><td style="padding:32px 36px 24px;">
      <p style="margin:0 0 6px;font-size:21px;font-weight:700;color:#ffffff;line-height:1.3;">
        {exam_title}
      </p>
      <p style="margin:0 0 24px;font-size:13px;color:rgba(255,255,255,0.4);">
        {course_code} — {course_title} &nbsp;·&nbsp; Set by {lecturer_name}
      </p>

      <!-- Info grid -->
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
                    border-radius:10px;overflow:hidden;margin-bottom:24px;">
        <tr>
          <td style="padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.05);width:50%;">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Starts</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{start_time}</p>
          </td>
          <td style="padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.05);">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Ends</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{end_time}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:12px 16px;">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Duration</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{duration_minutes} minutes</p>
          </td>
          <td style="padding:12px 16px;">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Total Marks</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{int(total_marks)}</p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 20px;font-size:13px;color:rgba(255,255,255,0.45);line-height:1.6;">
        Hi {first_name}, a new <strong style="color:#ffffff;">{type_label}</strong> has been
        posted for your course. Log in to MindStack to view the details and prepare.
      </p>

      <!-- CTA -->
      <table cellpadding="0" cellspacing="0">
        <tr>
          <td style="border-radius:9px;background:#ffffff;">
            <a href="{dashboard_url}"
               style="display:inline-block;padding:12px 28px;font-size:14px;
                      font-weight:700;color:#000000;text-decoration:none;border-radius:9px;">
              View on Dashboard
            </a>
          </td>
        </tr>
      </table>
    </td></tr>

    <!-- Footer -->
    <tr><td style="padding:18px 36px 24px;border-top:1px solid rgba(255,255,255,0.06);">
      <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.18);text-align:center;">
        &copy; 2026 MindStack &nbsp;·&nbsp; You are receiving this because you are enrolled in {course_code}
      </p>
    </td></tr>
  </table>

</td></tr>
</table>
</body>
</html>"""

    text = (
        f"Hi {first_name},\n\n"
        f"A new {type_label} has been posted.\n\n"
        f"Course:    {course_code} — {course_title}\n"
        f"Title:     {exam_title}\n"
        f"Set by:    {lecturer_name}\n"
        f"Starts:    {start_time}\n"
        f"Ends:      {end_time}\n"
        f"Duration:  {duration_minutes} minutes\n"
        f"Marks:     {int(total_marks)}\n\n"
        f"Log in to view it: {dashboard_url}\n\n"
        f"— MindStack Team"
    )

    return send_email(to_email, first_name, subject, html, text)


# ─────────────────────────── live class notification ───────────────────────────

def send_live_class_email(first_name: str, to_email: str,
                          class_title: str, class_description: str,
                          course_code: str, course_title: str,
                          lecturer_name: str,
                          platform: str, meeting_link: str,
                          scheduled_at: str, duration_minutes: int,
                          dashboard_url: str) -> tuple:
    """Notify an enrolled student that a live class has been scheduled."""

    platform_label = (platform or 'Online').title()
    platform_icons = {
        'zoom':   '🟦',
        'meet':   '🟩',
        'teams':  '🟪',
        'custom': '🔗',
    }
    platform_icon = platform_icons.get((platform or '').lower(), '🖥')

    subject = f"Live class scheduled — {course_code}: {class_title}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;min-height:100vh;">
<tr><td align="center" style="padding:48px 16px;">

  <table width="520" cellpadding="0" cellspacing="0"
         style="background:#111111;border:1px solid rgba(255,255,255,0.08);
                border-radius:16px;overflow:hidden;max-width:520px;width:100%;">

    <!-- Header -->
    <tr><td style="background:#000000;padding:24px 36px;border-bottom:1px solid rgba(255,255,255,0.06);">
      <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
        <tr>
          <td style="width:32px;height:32px;background:#ffffff;border-radius:7px;
                     text-align:center;vertical-align:middle;">
            <span style="font-size:16px;line-height:32px;">⚡</span>
          </td>
          <td style="padding-left:10px;font-size:20px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">MindStack</td>
        </tr>
      </table>
    </td></tr>

    <!-- Colour band for live class -->
    <tr><td style="background:rgba(34,197,94,0.10);border-bottom:1px solid rgba(34,197,94,0.18);
                   padding:10px 36px;">
      <span style="font-size:11px;font-weight:700;color:#86efac;text-transform:uppercase;
                   letter-spacing:1px;">{platform_icon} Live Class — {platform_label}</span>
    </td></tr>

    <!-- Body -->
    <tr><td style="padding:32px 36px 24px;">
      <p style="margin:0 0 6px;font-size:21px;font-weight:700;color:#ffffff;line-height:1.3;">
        {class_title}
      </p>
      <p style="margin:0 0 {('18px' if not class_description else '10px')};font-size:13px;
                color:rgba(255,255,255,0.4);">
        {course_code} — {course_title} &nbsp;·&nbsp; Hosted by {lecturer_name}
      </p>
      {'<p style="margin:0 0 18px;font-size:13px;color:rgba(255,255,255,0.55);line-height:1.6;">' + class_description + '</p>' if class_description else ''}

      <!-- Info grid -->
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
                    border-radius:10px;overflow:hidden;margin-bottom:24px;">
        <tr>
          <td style="padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.05);width:50%;">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Date &amp; Time</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{scheduled_at}</p>
          </td>
          <td style="padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.05);">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Duration</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{duration_minutes} minutes</p>
          </td>
        </tr>
        <tr>
          <td colspan="2" style="padding:12px 16px;">
            <p style="margin:0 0 3px;font-size:10px;color:rgba(255,255,255,0.3);
                      text-transform:uppercase;letter-spacing:0.6px;">Platform</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#ffffff;">{platform_label}</p>
          </td>
        </tr>
      </table>

      <!-- Meeting link box -->
      <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.15);
                  border-radius:9px;padding:14px 16px;margin-bottom:24px;">
        <p style="margin:0 0 4px;font-size:11px;color:rgba(134,239,172,0.7);
                  text-transform:uppercase;letter-spacing:0.5px;">Meeting Link</p>
        <a href="{meeting_link}"
           style="font-size:13px;color:#86efac;word-break:break-all;text-decoration:none;"
           >{meeting_link}</a>
      </div>

      <p style="margin:0 0 20px;font-size:13px;color:rgba(255,255,255,0.45);line-height:1.6;">
        Hi {first_name}, your lecturer has scheduled a live session.
        Make sure to join on time using the link above or the one on your dashboard.
      </p>

      <!-- CTA -->
      <table cellpadding="0" cellspacing="0">
        <tr>
          <td style="border-radius:9px;background:#ffffff;margin-right:10px;">
            <a href="{dashboard_url}"
               style="display:inline-block;padding:12px 28px;font-size:14px;
                      font-weight:700;color:#000000;text-decoration:none;border-radius:9px;">
              View on Dashboard
            </a>
          </td>
        </tr>
      </table>
    </td></tr>

    <!-- Footer -->
    <tr><td style="padding:18px 36px 24px;border-top:1px solid rgba(255,255,255,0.06);">
      <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.18);text-align:center;">
        &copy; 2026 MindStack &nbsp;·&nbsp; You are receiving this because you are enrolled in {course_code}
      </p>
    </td></tr>
  </table>

</td></tr>
</table>
</body>
</html>"""

    text = (
        f"Hi {first_name},\n\n"
        f"A live class has been scheduled for your course.\n\n"
        f"Course:    {course_code} — {course_title}\n"
        f"Title:     {class_title}\n"
        f"Host:      {lecturer_name}\n"
        f"Platform:  {platform_label}\n"
        f"When:      {scheduled_at}\n"
        f"Duration:  {duration_minutes} minutes\n"
        f"Link:      {meeting_link}\n\n"
        + (f"Details:\n{class_description}\n\n" if class_description else "")
        + f"View on dashboard: {dashboard_url}\n\n"
        f"— MindStack Team"
    )

    return send_email(to_email, first_name, subject, html, text)


# ─────────────────────────── helpers ───────────────────────────

def _strip_tags(html: str) -> str:
    """Minimal HTML tag stripper for plain-text fallback."""
    import re
    return re.sub(r'<[^>]+>', '', html or '')
