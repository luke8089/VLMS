"""
Email Configuration
SMTP settings for the MindStack LMS mailer.
"""

MAIL_CONFIG = {
    'smtp': {
        'host': 'smtp.gmail.com',
        'username': 'lukeedwin81@gmail.com',
        'password': 'bpklbnlrdvnqtlvf',
        'port': 587,
        'encryption': 'tls',   # 'tls' (STARTTLS on 587) or 'ssl' (SMTPS on 465)
        'auth': True,
    },
    'from': {
        'email': 'lukeedwin81@gmail.com',
        'name': 'MindStack LMS',
    },
    'admin': {
        'email': 'lukeedwin81@gmail.com',
        'name': 'MindStack Admin',
    },
    'base_url': 'http://localhost:5000',
}
