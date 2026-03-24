#!/usr/bin/env python3
"""Test HR Score Form Page"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import Application
from core.forms import HRScoreForm

print("🧪 Testing HR Score Form\n")

# Get an application that should have the HR Score button
apps = Application.objects.filter(status='hr_scheduled')
print(f"Applications in HR_SCHEDULED status: {apps.count()}\n")

if apps.exists():
    for app in apps:
        print(f"Testing Application ID {app.pk}: {app.candidate.username} -> {app.job.title}")
        print(f"  Status: {app.status}")
        print(f"  HR Attended: {app.hr_attended}")
        print(f"  HR Score: {app.hr_score}")
        print(f"  HR Feedback: {app.hr_feedback}\n")
        
        # Try to create the form
        form = HRScoreForm(instance=app)
        print(f"  Form fields: {list(form.fields.keys())}")
        print(f"  Form renders: {bool(str(form))}")
        print(f"  Form is valid (empty): {form.is_valid()}\n")
else:
    print("❌ No applications in hr_scheduled status!")
    print("\nAll applications:")
    for app in Application.objects.all():
        print(f"  ID {app.pk}: {app.candidate.username} - Status: {app.status}")
