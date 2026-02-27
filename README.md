# 🤖 RecruitAI - AI-Powered Recruitment System

A complete Django-based recruitment system using SBERT (Sentence-BERT) for intelligent resume matching and ranking.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database & Demo Data
```bash
python setup.py
```

### 3. Run Server
```bash
python manage.py runserver
```

### 4. Open Browser
Visit: **http://127.0.0.1:8000**

---

## 🔐 Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| HR/Admin | `hr_admin` | `admin123` |
| Candidate | `john_doe` | `cand123` |

---

## 🏗️ Project Structure

```
recruitment_ai/
├── manage.py
├── setup.py              ← Run this first
├── requirements.txt
├── recruitment_ai/
│   ├── settings.py
│   └── urls.py
└── core/
    ├── models.py         ← Database models
    ├── views.py          ← All views (HR + Candidate)
    ├── urls.py           ← URL routing
    ├── forms.py          ← Django forms
    ├── ai_engine.py      ← 🤖 SBERT AI core module
    ├── admin.py
    └── templates/core/
        ├── base.html
        ├── login.html
        ├── register.html
        ├── hr_dashboard.html
        ├── job_form.html
        ├── job_applicants.html
        ├── application_detail_hr.html
        ├── candidate_dashboard.html
        ├── job_list.html
        ├── apply_job.html
        ├── application_status.html
        └── hr_reports.html
```

---

## 🧠 AI Engine (core/ai_engine.py)

### Phase 4: Text Processing Pipeline

**Step 1 - Text Cleaning:**
- Remove URLs, emails, special characters
- Normalize whitespace
- Lowercase

**Step 2 - SBERT Embedding:**
- Model: `all-MiniLM-L6-v2`
- Output: 384-dimensional vectors

**Step 3 - Cosine Similarity:**
```
Similarity = (A · B) / (||A|| × ||B||)
```

### Phase 5: Auto-Shortlisting
- Score ≥ 0.60 → **Shortlisted** ✅
- Score < 0.60 → **Not Shortlisted** ❌

### Phase 8: Final Score Formula
```
Final Score = (0.6 × SBERT Similarity) + (0.4 × Interview Score/10)
```

---

## 📊 Features by Phase

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | User Auth (HR + Candidate) | ✅ |
| 2 | Job Creation (HR) | ✅ |
| 3 | Resume Upload + Text Extraction | ✅ |
| 4 | SBERT Embeddings + Cosine Similarity | ✅ |
| 5 | Auto Shortlisting (threshold: 0.60) | ✅ |
| 6 | Resume Ranking (sorted by score) | ✅ |
| 7 | Interview Tracking (5 stages) | ✅ |
| 8 | Final Score (weighted formula) | ✅ |
| 9 | Selection/Rejection Decision | ✅ |
| 10 | Reports & History | ✅ |

---

## 🔐 Access Control

| Candidate Status | Can See |
|-----------------|---------|
| Applied | Submission confirmation |
| Not Shortlisted | Rejection message |
| Shortlisted | Interview info |
| HR/Tech/Final Interview | Schedule + updates |
| Selected | Offer message |
| Rejected | Rejection message |

---

## 🛠️ Tech Stack

- **Backend:** Django 4.2
- **AI:** sentence-transformers (SBERT `all-MiniLM-L6-v2`)
- **Similarity:** scikit-learn / NumPy cosine similarity
- **PDF:** PyMuPDF (fitz)
- **DOCX:** python-docx
- **Database:** SQLite (development) → PostgreSQL (production)
- **Frontend:** Pure HTML/CSS (no framework required)
