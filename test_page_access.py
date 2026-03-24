#!/usr/bin/env python3
"""Test accessing HR Score page via Django test client"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Application

print("🧪 Testing HR Score Page Access\n")

# Create test client
client = Client()

# Get HR user and login
hr_user = User.objects.get(username='hr_admin')
print(f"HR User: {hr_user.username}")
logged_in = client.login(username='hr_admin', password='admin123')
print(f"Login successful: {logged_in}\n")

# Try to access HR score page for an application
apps = Application.objects.filter(status='hr_scheduled')
if apps.exists():
    app = apps.first()
    print(f"Testing application ID {app.pk}: {app.candidate.username}\n")
    
    response = client.get(f'/hr/applications/{app.pk}/hr-score/')
    print(f"Response Status: {response.status_code}")
    print(f"Response Content-Type: {response.get('Content-Type')}")
    print(f"Response Length: {len(response.content)} bytes\n")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        # Check if key elements are in the response
        checks = {
            'form tag': '<form' in content,
            'hr_score field': 'hr_score' in content,
            'hr_attended field': 'hr_attended' in content,
            'hr_feedback field': 'hr_feedback' in content,
            'submit button': 'submit' in content or 'Save' in content,
            'application info': app.candidate.username in content,
        }
        
        print("Content checks:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
        
        if not all(checks.values()):
            print("\n⚠️  Some content is missing! Showing first 2000 chars:")
            print(content[:2000])
    else:
        print(f"Error Response:\n{response.content.decode('utf-8')[:500]}")
else:
    print("❌ No applications in hr_scheduled status")
