from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [('hr', 'HR/Admin'), ('candidate', 'Candidate')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_hr(self):
        return self.role == 'hr'

    def is_candidate(self):
        return self.role == 'candidate'


class Job(models.Model):
    hr = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    required_skills = models.TextField(help_text="Comma-separated skills")
    required_experience = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_skills_list(self):
        return [s.strip() for s in self.required_skills.split(',')]

    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        return True


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('not_shortlisted', 'Not Shortlisted'),
        ('shortlisted', 'Shortlisted'),
        ('technical_scheduled', 'Technical Interview Scheduled'),
        ('technical_completed', 'Technical Interview Completed'),
        ('hr_scheduled', 'HR Interview Scheduled'),
        ('hr_completed', 'HR Interview Completed'),
        ('system_recommended', 'System Recommended'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    RECOMMENDATION_CHOICES = [
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    # Basic
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    resume_text = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='applied')
    rank = models.IntegerField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Phase 4 - Resume AI Score
    resume_score = models.FloatField(null=True, blank=True)

    # Phase 5 - Technical Interview
    technical_date = models.DateField(null=True, blank=True)
    technical_score = models.FloatField(null=True, blank=True)
    technical_attended = models.BooleanField(null=True, blank=True)
    technical_feedback = models.TextField(blank=True)

    # Phase 6 - HR Interview
    hr_date = models.DateField(null=True, blank=True)
    hr_score = models.FloatField(null=True, blank=True)
    hr_attended = models.BooleanField(null=True, blank=True)
    hr_feedback = models.TextField(blank=True)

    # Phase 7 - Final Score
    final_score = models.FloatField(null=True, blank=True)
    system_recommendation = models.CharField(
        max_length=10, choices=RECOMMENDATION_CHOICES, null=True, blank=True
    )

    # Phase 8 - HR Final Decision
    final_decision = models.CharField(
        max_length=10, choices=RECOMMENDATION_CHOICES, null=True, blank=True
    )
    hr_decision_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-resume_score']

    def __str__(self):
        return f"{self.candidate.username} → {self.job.title}"

    def compute_final_score(self):
        """
        Final Score = (0.6 × Resume Score) + (0.3 × Technical Score) + (0.1 × HR Score)
        """
        if (self.resume_score is not None and
                self.technical_score is not None and
                self.hr_score is not None):
            self.final_score = (
                (0.6 * self.resume_score) +
                (0.3 * (self.technical_score / 10)) +
                (0.1 * (self.hr_score / 10))
            )
            # Auto system recommendation
            if self.final_score >= 0.6:
                self.system_recommendation = 'selected'
            else:
                self.system_recommendation = 'rejected'
            self.status = 'system_recommended'
            self.save()
        return self.final_score

    def can_see_technical(self):
        return self.status in [
            'technical_scheduled', 'technical_completed',
            'hr_scheduled', 'hr_completed',
            'system_recommended', 'selected', 'rejected'
        ]

    def can_see_hr_interview(self):
        return self.status in [
            'hr_scheduled', 'hr_completed',
            'system_recommended', 'selected', 'rejected'
        ]

    def can_see_final(self):
        return self.status in ['system_recommended', 'selected', 'rejected']


class InterviewNote(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    stage = models.CharField(max_length=50)
    note = models.TextField()
    score = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.application} - {self.stage}"