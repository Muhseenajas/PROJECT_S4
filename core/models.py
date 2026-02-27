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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_skills_list(self):
        return [s.strip() for s in self.required_skills.split(',')]


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('not_shortlisted', 'Not Shortlisted'),
        ('shortlisted', 'Shortlisted'),
        ('hr_interview', 'HR Interview'),
        ('technical_interview', 'Technical Interview'),
        ('final_interview', 'Final Interview'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    resume_text = models.TextField(blank=True)
    similarity_score = models.FloatField(null=True, blank=True)
    interview_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='applied')
    hr_notes = models.TextField(blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-similarity_score']

    def __str__(self):
        return f"{self.candidate.username} → {self.job.title}"

    def can_see_interview(self):
        return self.status in ['shortlisted', 'hr_interview', 'technical_interview',
                               'final_interview', 'selected', 'rejected']

    def can_see_schedule(self):
        return self.status in ['hr_interview', 'technical_interview', 'final_interview']

    def compute_final_score(self):
        if self.similarity_score is not None and self.interview_score is not None:
            self.final_score = (0.6 * self.similarity_score) + (0.4 * (self.interview_score / 10))
            self.save()
        return self.final_score


class InterviewNote(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    stage = models.CharField(max_length=50)
    note = models.TextField()
    score = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.application} - {self.stage}"
