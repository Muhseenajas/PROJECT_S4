from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # HR - Jobs
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/jobs/create/', views.create_job, name='create_job'),
    path('hr/jobs/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('hr/jobs/<int:pk>/applicants/', views.job_applicants, name='job_applicants'),
    path('hr/jobs/<int:job_pk>/process-all/', views.process_all_ai, name='process_all_ai'),
    path('hr/reports/', views.hr_reports, name='hr_reports'),

    # HR - Application Detail
    path('hr/applications/<int:pk>/', views.application_detail_hr, name='application_detail_hr'),

    # Phase 4 - Shortlist
    path('hr/applications/<int:pk>/shortlist/', views.shortlist_candidate, name='shortlist_candidate'),

    # Phase 5 - Technical Interview
    path('hr/applications/<int:pk>/schedule-technical/', views.schedule_technical, name='schedule_technical'),
    path('hr/applications/<int:pk>/technical-score/', views.enter_technical_score, name='enter_technical_score'),

    # Phase 6 - HR Interview
    path('hr/applications/<int:pk>/schedule-hr/', views.schedule_hr_interview, name='schedule_hr_interview'),
    path('hr/applications/<int:pk>/hr-score/', views.enter_hr_score, name='enter_hr_score'),

    # Phase 8 - Final Decision
    path('hr/applications/<int:pk>/final-decision/', views.final_decision, name='final_decision'),

    # Candidate
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('candidate/applications/<int:pk>/', views.application_status, name='application_status'),
]