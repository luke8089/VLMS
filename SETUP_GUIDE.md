# MindStack VLMS — Setup Guide

A complete start-to-finish guide for running this project on a new machine.
Follow each step in order.

---

## 1) Prerequisites

Install the following before cloning the project:

### 1.1 Git
- Download: https://git-scm.com/downloads
- Verify: `git --version`

### 1.2 Python 3.11
- Download: https://www.python.org/downloads/
- Enable **Add Python to PATH** during install.
- Verify: `python --version`

### 1.3 XAMPP (MySQL)
- Download: https://www.apachefriends.org/download.html
- Open **XAMPP Control Panel** and start **MySQL**.
- Apache is not required for this Flask app.

### 1.4 Microsoft Visual C++ Build Tools (Windows)
- Required to compile `mysqlclient`.
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install workload: **Desktop development with C++**.

### 1.5 Google Gemini API Key (required for AI features)
- Go to: https://aistudio.google.com/app/apikey
- Click **Create API Key** and copy the key.
- Free tier: 15 requests/min, 500 requests/day — sufficient for normal use.
- Paste the key into your `.env` file (see Step 6).

### 1.6 Tesseract OCR (optional — for scanned PDFs)
- Required to extract text from image-based PDFs.
  ```powershell
  winget install --id UB-Mannheim.TesseractOCR -e
  ```

---

## 2) Clone the Project

```powershell
git clone https://github.com/luke8089/VLMS.git
cd VLMS
```

To use the latest feature branch instead of main:

```powershell
git checkout feature/gemini-ai-grading-and-course-disable
```

---

## 3) Create and Activate Virtual Environment

```powershell
python -m venv .venv
```

Activate:

- **PowerShell**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Command Prompt**
  ```bat
  .\.venv\Scripts\activate.bat
  ```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

---

## 4) Install Dependencies

```powershell
pip install -r requirements.txt
```

> First install can take a few minutes due to `torch` and `opencv-python`.
> If `mysqlclient` fails, ensure Visual C++ Build Tools (step 1.4) are installed.

---

## 5) Create the MySQL Database

Ensure XAMPP MySQL is running, then create the database:

### Via phpMyAdmin
1. Open `http://localhost/phpmyadmin`
2. Click **New**
3. Database name: `aura_edu`
4. Collation: `utf8mb4_general_ci`
5. Click **Create**

### Via SQL
```sql
CREATE DATABASE aura_edu CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

---

## 6) Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=change-this-secret-key
JWT_SECRET_KEY=change-this-jwt-secret
DATABASE_URL=mysql://root:@localhost/aura_edu
FLASK_ENV=development
FLASK_DEBUG=1

# Google Gemini AI (required for AI features)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash

# OCR (optional)
OCR_MAX_PAGES=5
OCR_SCALE=1.5
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

If MySQL `root` has a password:
```env
DATABASE_URL=mysql://root:YOUR_PASSWORD@localhost/aura_edu
```

---

## 7) Run the App

```powershell
python app.py
```

On first run the app will:
- Create all database tables automatically
- Seed a default admin account
- Start the server at `http://localhost:5000`

---

## 8) Database Migrations (existing installations only)

If you are upgrading an existing `aura_edu` database, run these SQL statements to add the columns introduced in recent updates:

```sql
-- Course soft-disable feature
ALTER TABLE courses ADD COLUMN IF NOT EXISTS is_active TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE courses ADD COLUMN IF NOT EXISTS disabled_at DATETIME NULL;

-- Exam reschedule tracking
ALTER TABLE exams ADD COLUMN IF NOT EXISTS rescheduled_at DATETIME NULL;
```

Run via XAMPP phpMyAdmin SQL tab, or via the MySQL CLI:

```powershell
C:\xampp\mysql\bin\mysql.exe -u root aura_edu -e "
ALTER TABLE courses ADD COLUMN IF NOT EXISTS is_active TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE courses ADD COLUMN IF NOT EXISTS disabled_at DATETIME NULL;
ALTER TABLE exams ADD COLUMN IF NOT EXISTS rescheduled_at DATETIME NULL;
"
```

Fresh installs (no existing database) do **not** need this step — the tables are created correctly on first run.

---

## 9) Default Accounts

| Role     | Email                      | Password      |
|----------|----------------------------|---------------|
| Admin    | admin@gmail.com            | 111Admin@     |
| Lecturer | lec@gmail.com              | 111Lec@@      |

> Change credentials after first login via the admin panel.

---

## 10) AI Features (Google Gemini)

The app uses Google Gemini 2.5 Flash for:

- **Document summarization** — summaries when reading uploaded materials
- **Exam question generation** — generates questions from course content
- **Automated exam marking** — grades short-answer and essay questions
- **Violation analysis** — AI narrative risk reports from proctoring data
- **AI recommendations** — personalised study recommendations per student

Grading runs in a **background thread** after submission so the student never waits. If Gemini is unavailable (rate limit or network error), the system falls back to NLP-based cosine-similarity grading automatically.

### Free tier limits
| Limit | Value |
|-------|-------|
| Requests per minute | 15 |
| Tokens per minute | 1,000,000 |
| Requests per day | 500 |

---

## 11) Face Registration & Exam Proctoring

Students must register their face before sitting a proctored exam:

- Navigate to `http://localhost:5000/face-registration`
- Capture 3 samples (front, left, right)
- Face verification runs at exam start and during the exam

Proctoring captures:
- Screenshots stored in `screenshots/` (local only, not committed to git)
- Screen recordings stored in `recordings/` (local only, not committed to git)

---

## 12) Feature Overview

### Roles
| Role | Access |
|------|--------|
| Admin | Full platform management, user management, course oversight |
| Lecturer | Create and manage their own courses, exams, and materials |
| Student | Enrol in courses, take exams, view grades and AI recommendations |

### Course Management
- Lecturers can **disable** a unit — students immediately lose access to all materials, exams, and content
- Admins can **restore** a disabled unit or **permanently delete** it
- Disabled courses are visible only in the admin panel with a restore option

### Exam Reschedule
- Admins and lecturers can **reschedule** any exam after its end time has passed
- The Reschedule button only appears on exam cards once the exam window has closed
- On reschedule: `in_progress` submissions (students who started but never submitted) are **automatically cleared** so those students get a fresh attempt
- Students who already **submitted** are permanently locked out from rescheduled exams — they cannot retake it
- Rescheduled exams show a blue **"Rescheduled"** badge on the student dashboard
- Admins can additionally reset specific submitted students' attempts when rescheduling

### Exam Proctoring & Violations
- Live face verification, eye tracking, and tab-switch detection during exams
- Violations are logged and scored in real time
- Lecturers and admins can trigger AI-generated violation analysis reports per submission

---

## 13) Daily Run Commands

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

---

## 14) Troubleshooting

### PowerShell blocks venv activation
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `ModuleNotFoundError: No module named 'MySQLdb'`
- Ensure venv is activated, then: `pip install -r requirements.txt`
- Ensure Visual C++ Build Tools are installed.

### `Access denied for user 'root'@'localhost'`
- Update `DATABASE_URL` in `.env` with the correct MySQL password.

### `Can't connect to MySQL server on 'localhost'`
- Start MySQL in XAMPP Control Panel.

### Port 5000 already in use
- Stop the conflicting process or change the port in `app.py`.

### AI features not working (Gemini 429 / rate limit)
- The free tier allows 15 requests/minute. Heavy simultaneous use may briefly hit this.
- Exam grading runs in the background — submissions still succeed even if Gemini is rate-limited.
- The system automatically falls back to NLP grading when Gemini is unavailable.

### AI features returning errors
- Confirm `GEMINI_API_KEY` is set correctly in `.env`.
- Confirm `GEMINI_MODEL=gemini-2.5-flash` is set.
- Test your key at: https://aistudio.google.com/app/apikey

### OCR not working on scanned PDFs
- Confirm Tesseract is installed.
- Check `TESSERACT_CMD` path in `.env`.

### Course delete fails with integrity error
- This was a known issue (missing cascade on `learning_progress`). Fixed in the current version.
- If still occurring on an old install, run: `pip install -r requirements.txt` to ensure the latest code is active.

---

## 15) Setup Checklist

- [ ] Python 3.11 installed
- [ ] `.venv` created and activated
- [ ] `pip install -r requirements.txt` succeeded
- [ ] XAMPP MySQL is running
- [ ] Database `aura_edu` exists
- [ ] `.env` file created with `GEMINI_API_KEY` set
- [ ] `python app.py` starts without errors
- [ ] Login works at `http://localhost:5000`
- [ ] Face registration works at `http://localhost:5000/face-registration`
- [ ] DB migrations run (existing installs only — Step 8)
- [ ] Tesseract installed (optional — for scanned PDFs)

---

## 16) Project Structure

```
VLMS/
├── app.py                    # Flask entry point
├── config.py                 # App configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
│
├── database/
│   ├── models.py             # SQLAlchemy models
│   └── db_init.py            # DB initialisation & seeding
│
├── routes/
│   ├── auth_routes.py        # Login, register, face registration
│   ├── student_routes.py     # Student dashboard & exam portal
│   ├── lecturer_routes.py    # Lecturer panel, exams, reschedule
│   ├── exam_routes.py        # Exam submission handling
│   ├── admin_routes.py       # Admin management, course delete, reschedule
│   └── analytics_routes.py  # Analytics & AI recommendations API
│
├── services/
│   ├── authentication_service.py
│   ├── analytics_service.py
│   └── exam_service.py       # Gemini-powered auto-grading
│
├── ai_modules/
│   ├── gemini_service.py          # Google Gemini integration (primary AI)
│   ├── assessment_ai/             # Quiz generation, NLP essay grading (fallback)
│   ├── exam_proctoring/           # Face auth, risk scoring, eye tracking
│   └── learning_ai/               # Flashcards, summarizer, adaptive learning
│
├── templates/                # Jinja2 HTML templates
│   ├── admin_panel.html      # Admin dashboard (modals, toasts, course/exam mgmt)
│   ├── lecturer_panel.html   # Lecturer dashboard (exam reschedule)
│   └── student_panel.html    # Student dashboard (rescheduled badge, lock-out)
│
├── static/                   # Static JS assets
│
├── landing/                  # Public landing page
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/
│
├── mail/                     # Email service (OAuth mailer)
│
├── uploads/                  # User-uploaded files (not committed)
│   ├── courses/
│   └── profiles/
│
├── screenshots/              # Proctoring screenshots (not committed)
└── recordings/               # Proctoring recordings (not committed)
```
