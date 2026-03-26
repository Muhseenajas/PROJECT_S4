import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
django.setup()

from core.models import Application

for a in Application.objects.all():
    print(f'{a.pk}: {a.status} - {a.candidate.email}')