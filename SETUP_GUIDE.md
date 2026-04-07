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

### 1.5 Ollama (optional — for AI features)
- Download: https://ollama.com/download
- After install, pull a model:
  ```powershell
  ollama pull llama3.2:1b
  ```
- `llama3` or `mistral` also work (larger, higher quality):
  ```powershell
  ollama pull mistral
  ```

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
OLLAMA_MODEL=llama3.2:1b
OLLAMA_TIMEOUT=15
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

## 8) Default Admin Login

| Role  | Email           | Password  |
|-------|-----------------|-----------|
| Admin | admin@gmail.com | 111Admin@ |

> Change credentials after first login.

---

## 9) AI Features (Ollama)

The app uses a locally-running Ollama instance for:
- Document summarization when uploading course materials
- Exam question generation from course content
- AI response time is tracked and displayed in the Admin panel

To use AI features:
1. Start Ollama
2. Confirm it's reachable at `http://localhost:11434`
3. Ensure at least one model is pulled (recommended: `llama3.2:1b`)

If Ollama is not running, the app continues to work — AI features fall back gracefully.

---

## 10) Face Registration & Exam Proctoring

Students must register their face before sitting a proctored exam:

- Navigate to `http://localhost:5000/face-registration`
- Capture 3 samples (front, left, right)
- Face verification runs at exam start and during the exam

Proctoring captures:
- Screenshots stored in `screenshots/` (local only, not committed to git)
- Screen recordings stored in `recordings/` (local only, not committed to git)

---

## 11) Daily Run Commands

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

---

## 12) Troubleshooting

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

### AI features not working
- Ensure Ollama is running and a model is pulled:
  ```powershell
  ollama pull llama3.2:1b
  ```

### OCR not working on scanned PDFs
- Confirm Tesseract is installed.
- Check `TESSERACT_CMD` path in `.env`.

---

## 13) Setup Checklist

- [ ] Python 3.11 installed
- [ ] `.venv` created and activated
- [ ] `pip install -r requirements.txt` succeeded
- [ ] XAMPP MySQL is running
- [ ] Database `aura_edu` exists
- [ ] `.env` file created in project root
- [ ] `python app.py` starts without errors
- [ ] Login works at `http://localhost:5000`
- [ ] Face registration works at `http://localhost:5000/face-registration`
- [ ] Ollama running (optional — for AI features)
- [ ] Tesseract installed (optional — for scanned PDFs)

---

## 14) Project Structure

```
VLMS/
├── app.py                    # Flask entry point
├── config.py                 # App configuration
├── requirements.txt          # Python dependencies
├── _migrate.py               # DB migration helper (existing installs)
├── .env                      # Environment variables (not committed)
│
├── database/
│   ├── models.py             # SQLAlchemy models
│   └── db_init.py            # DB initialisation & seeding
│
├── routes/
│   ├── auth_routes.py        # Login, register, face registration
│   ├── student_routes.py     # Student dashboard & portal
│   ├── lecturer_routes.py    # Lecturer panel & content
│   ├── exam_routes.py        # Exam creation & submission
│   ├── admin_routes.py       # Admin management
│   └── analytics_routes.py  # Analytics & reporting API
│
├── services/
│   ├── authentication_service.py
│   ├── analytics_service.py
│   └── exam_service.py
│
├── ai_modules/
│   ├── ollama_service.py          # LLM integration (summarization, Q gen)
│   ├── assessment_ai/             # Quiz generation, essay grading
│   ├── exam_proctoring/           # Face auth, risk scoring, eye tracking
│   └── learning_ai/               # Flashcards, summarizer, adaptive learning
│
├── templates/                # Jinja2 HTML templates
├── static/                   # Static JS assets
│
├── landing/                  # Public landing page
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/               # Landing page images
│
├── mail/                     # Email service (OAuth mailer)
├── migrations/               # SQL schema reference
│
├── uploads/                  # User-uploaded files (not committed)
│   ├── courses/
│   └── profiles/
│
├── screenshots/              # Proctoring screenshots (not committed)
└── recordings/               # Proctoring recordings (not committed)
```
