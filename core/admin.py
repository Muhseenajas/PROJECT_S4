from django.contrib import admin
from .models import UserProfile, Job, Application, InterviewNote


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'hr', 'start_date', 'end_date', 'created_at']
    list_filter = ['start_date', 'end_date']
    search_fields = ['title', 'required_skills']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'similarity_score', 'final_score', 'rank', 'applied_at']
    list_filter = ['status']
    search_fields = ['candidate__username', 'job__title']
    readonly_fields = ['similarity_score', 'final_score', 'rank']


@admin.register(InterviewNote)
class InterviewNoteAdmin(admin.ModelAdmin):
    list_display = ['application', 'stage', 'score', 'created_by', 'created_at']
