#!/usr/bin/env python3
"""
RecruitAI - Quick Setup Script
Run this once after installing dependencies to initialize the database.
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from core.models import UserProfile, Job

print("🔧 Running migrations...")
call_command('makemigrations', 'core')
call_command('migrate')

print("\n👤 Creating demo accounts...")

# HR User
if not User.objects.filter(username='hr_admin').exists():
    hr_user = User.objects.create_user(
        username='hr_admin',
        password='admin123',
        first_name='Sarah',
        last_name='Johnson',
        email='hr@company.com'
    )
    UserProfile.objects.create(user=hr_user, role='hr', phone='+91-9876543210')
    print("  ✅ HR Account: username=hr_admin, password=admin123")

# Candidate User
if not User.objects.filter(username='john_doe').exists():
    cand_user = User.objects.create_user(
        username='john_doe',
        password='cand123',
        first_name='John',
        last_name='Doe',
        email='john@email.com'
    )
    UserProfile.objects.create(user=cand_user, role='candidate', phone='+91-9876543211')
    print("  ✅ Candidate Account: username=john_doe, password=cand123")

# Demo Job
hr = User.objects.get(username='hr_admin')
if not Job.objects.filter(title='Senior Python Developer').exists():
    Job.objects.create(
        hr=hr,
        title='Senior Python Developer',
        required_skills='Python, Django, REST API, PostgreSQL, Docker, Machine Learning',
        required_experience='3-5 years',
        description="""We are looking for an experienced Python Developer to join our growing team.

Responsibilities:
- Design and implement scalable web applications using Django
- Build and maintain REST APIs
- Collaborate with data science team on ML integration
- Code review and mentoring junior developers
- Database design and optimization

Requirements:
- Strong Python programming skills
- Experience with Django and Django REST Framework
- Knowledge of SQL databases (PostgreSQL preferred)
- Understanding of machine learning concepts
- Experience with Docker and CI/CD pipelines
- Excellent problem-solving skills
- Good communication skills""",
        is_active=True
    )
    print("  ✅ Demo job created: Senior Python Developer")

print("""
✅ Setup complete!

🚀 Start the server:
   python manage.py runserver

🌐 Open: http://127.0.0.1:8000

📋 Demo Accounts:
   HR:        hr_admin / admin123
   Candidate: john_doe / cand123
""")
