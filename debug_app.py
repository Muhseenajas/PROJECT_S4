#!/usr/bin/env python3
"""Debug script to reprocess stuck application"""
import os
import django
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import Application
from core.ai_engine import process_application

print("🔍 Debugging Application Processing\n")

# Get the stuck application
app = Application.objects.get(id=3)
print(f"Application: {app.candidate.username} -> {app.job.title}")
print(f"Resume file: {app.resume}")
print(f"Resume text exists: {bool(app.resume_text)}")
print(f"Current resume_score: {app.resume_score}\n")

try:
    print("Attempting to process...")
    score = process_application(app)
    print(f"✅ SUCCESS! Score: {score}")
    print(f"New resume_score in DB: {Application.objects.get(id=3).resume_score}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    traceback.print_exc()
