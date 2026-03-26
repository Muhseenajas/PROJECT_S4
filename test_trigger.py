import os
import django
from django.core.mail import send_mail
from django.conf import settings

print("Starting script")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_ai.settings')
django.setup()

from core.models import Application

print("Getting application")
a = Application.objects.get(pk=6)
print(f"Current status: {a.status}")
a.status = 'hr_scheduled'
a.save()
print(f"New status: {a.status}")

candidate_email = a.candidate.email
print(f"Candidate email: {candidate_email}")
if candidate_email:
    subject = f"HR Interview Scheduled - {a.job.title}"
    message = (
        f"Dear {a.candidate.first_name or a.candidate.username},\n\n"
        f"Congratulations! You have passed the technical interview and been selected for the HR interview for the role '{a.job.title}'.\n"
        f"Your Technical Score: {a.technical_score}/10\n\n"
        f"HR Interview Date: {a.hr_date.strftime('%Y-%m-%d') if a.hr_date else 'TBD'}\n"
        f"HR Interview Time: {a.hr_time.strftime('%H:%M') if a.hr_time else 'TBD'}\n"
        f"Interviewer: {a.hr_interviewer or 'TBD'}\n\n"
        f"Please be ready and join on time. We look forward to speaking with you soon.\n\n"
        f"Best regards,\n{a.job.hr.get_full_name() or a.job.hr.username}"
    )
    print("Sending email...")
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [candidate_email], fail_silently=False)
        print(f"HR interview scheduled and email sent to {candidate_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
else:
    print("No email address on file.")