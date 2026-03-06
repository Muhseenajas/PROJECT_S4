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

    # HR
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/jobs/create/', views.create_job, name='create_job'),
    path('hr/jobs/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('hr/jobs/<int:pk>/applicants/', views.job_applicants, name='job_applicants'),
    path('hr/jobs/<int:job_pk>/process-all/', views.process_all_ai, name='process_all_ai'),
    path('hr/applications/<int:pk>/', views.application_detail_hr, name='application_detail_hr'),
    path('hr/applications/<int:pk>/process/', views.process_ai, name='process_ai'),
    path('hr/reports/', views.hr_reports, name='hr_reports'),

    # Candidate
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('candidate/applications/<int:pk>/', views.application_status, name='application_status'),
]