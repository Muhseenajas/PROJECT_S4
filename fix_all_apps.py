#!/usr/bin/env python3
"""Check for stuck applications"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import Application
from core.ai_engine import process_application

stuck_apps = Application.objects.filter(resume_score__isnull=True)
print(f'Applications with NULL resume_score: {stuck_apps.count()}\n')

if stuck_apps.exists():
    for app in stuck_apps:
        print(f"Reprocessing ID {app.id}: {app.candidate.username} -> {app.job.title}")
        try:
            score = process_application(app)
            print(f"  ✅ Fixed! New score: {score}\n")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")
else:
    print("✅ All applications have been processed!")
