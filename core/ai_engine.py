"""
AI Processing Module - SBERT Embedding + Cosine Similarity
Uses sentence-transformers (all-MiniLM-L6-v2) for 384-dim embeddings
"""
import re
import io
import logging

logger = logging.getLogger(__name__)

# ── Text Extraction ──────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def extract_resume_text(file_path: str) -> str:
    """Auto-detect file type and extract text."""
    file_path = str(file_path)
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return ""


# ── Text Cleaning ────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Phase 4 Step 1: Text Cleaning
    - Remove special characters and symbols
    - Normalize whitespace
    - Lowercase
    """
    if not text:
        return ""
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # Remove special characters except alphanumeric and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\.,\-]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Lowercase
    text = text.lower()
    return text


# ── Embedding Generation ─────────────────────────────────────────────────────

_model = None

def get_sbert_model():
    """Load SBERT model (cached singleton)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SBERT model loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load SBERT model: {e}")
            raise
    return _model


def generate_embedding(text: str):
    """
    Phase 4 Step 2: Generate 384-dimensional SBERT embedding.
    Returns numpy array.
    """
    model = get_sbert_model()
    cleaned = clean_text(text)
    embedding = model.encode(cleaned, convert_to_numpy=True)
    return embedding


# ── Cosine Similarity ────────────────────────────────────────────────────────

def cosine_similarity(vec_a, vec_b) -> float:
    """
    Phase 4 Step 3: Cosine Similarity
    Similarity = (A · B) / (||A|| × ||B||)
    Returns value between 0 and 1.
    """
    import numpy as np
    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


# ── Main Matching Pipeline ───────────────────────────────────────────────────

SHORTLIST_THRESHOLD = 0.60  # Phase 5

def compute_similarity(job_text: str, resume_text: str) -> float:
    """
    Full pipeline:
    1. Clean texts
    2. Generate SBERT embeddings
    3. Compute cosine similarity
    Returns similarity score (0–1).
    """
    job_embedding = generate_embedding(job_text)
    resume_embedding = generate_embedding(resume_text)
    score = cosine_similarity(job_embedding, resume_embedding)
    return round(score, 4)


def get_job_full_text(job) -> str:
    """Combine job fields into single text for embedding."""
    return f"{job.title} {job.required_skills} {job.required_experience} {job.description}"


def determine_status(score: float) -> str:
    """Phase 5: Automatic Shortlisting."""
    if score >= SHORTLIST_THRESHOLD:
        return 'shortlisted'
    return 'not_shortlisted'


def process_application(application) -> float:
    """
    Full AI processing for a single application:
    1. Extract resume text (if not already done)
    2. Compute similarity score
    3. Update status
    4. Save application
    Returns similarity score.
    """
    from django.conf import settings
    import os

    # Extract resume text if needed
    if not application.resume_text:
        file_path = os.path.join(settings.MEDIA_ROOT, str(application.resume))
        application.resume_text = extract_resume_text(file_path)

    # Get job text
    job_text = get_job_full_text(application.job)

    # Compute similarity
    score = compute_similarity(job_text, application.resume_text)
    application.similarity_score = score

    # Auto-shortlist
    if application.status == 'applied':
        application.status = determine_status(score)

    application.save()
    return score


def rank_applicants_for_job(job) -> list:
    """
    Phase 6: Resume Ranking
    Returns applications sorted by similarity score (descending).
    Updates rank field for each application.
    """
    applications = list(job.applications.all())
    applications.sort(key=lambda a: a.similarity_score or 0, reverse=True)

    for rank, app in enumerate(applications, start=1):
        app.rank = rank
        app.save(update_fields=['rank'])

    return applications
