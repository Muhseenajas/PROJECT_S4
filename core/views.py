from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Q
from django.db import models
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserProfile, Job, Application, InterviewNote
from .forms import RegisterForm, JobForm, ResumeUploadForm, InterviewUpdateForm, InterviewNoteForm, ProfileUpdateForm
from .ai_engine import process_application, rank_applicants_for_job


# ── Helpers ──────────────────────────────────────────────────────────────────

def require_hr(func):
    """Decorator: requires HR role."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_hr():
            messages.error(request, "Access denied. HR only.")
            return redirect('dashboard')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def require_candidate(func):
    """Decorator: requires candidate role."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_candidate():
            messages.error(request, "Access denied. Candidates only.")
            return redirect('dashboard')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ── Auth Views ───────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}!")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_hr():
        return redirect('hr_dashboard')
    return redirect('candidate_dashboard')


# ── Profile Views ─────────────────────────────────────────────────────────────

@login_required
def view_profile(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'core/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('view_profile')
    else:
        form = ProfileUpdateForm(instance=request.user, profile=profile)
    return render(request, 'core/edit_profile.html', {'form': form})


# ── HR Views ─────────────────────────────────────────────────────────────────

@require_hr
def hr_dashboard(request):
    jobs = Job.objects.filter(hr=request.user).annotate(
        total=Count('applications'),
        shortlisted=Count('applications', filter=Q(applications__status='shortlisted')),
        selected=Count('applications', filter=Q(applications__status='selected')),
    )
    total_apps = Application.objects.filter(job__hr=request.user).count()
    shortlisted = Application.objects.filter(job__hr=request.user, status='shortlisted').count()
    selected = Application.objects.filter(job__hr=request.user, status='selected').count()
    rejected = Application.objects.filter(job__hr=request.user, status__in=['not_shortlisted', 'rejected']).count()

    context = {
        'jobs': jobs,
        'total_apps': total_apps,
        'shortlisted': shortlisted,
        'selected': selected,
        'rejected': rejected,
    }
    return render(request, 'core/hr_dashboard.html', context)


@require_hr
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.hr = request.user
            job.save()
            messages.success(request, f"Job '{job.title}' created successfully!")
            return redirect('hr_dashboard')
    else:
        form = JobForm()
    return render(request, 'core/job_form.html', {'form': form, 'title': 'Create Job'})


@require_hr
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, hr=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated!")
            return redirect('hr_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'core/job_form.html', {'form': form, 'title': 'Edit Job', 'job': job})


@require_hr
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, hr=request.user)
    applications = job.applications.select_related('candidate', 'candidate__profile').order_by('-similarity_score')
    return render(request, 'core/job_applicants.html', {'job': job, 'applications': applications})


@require_hr
def application_detail_hr(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)

    if request.method == 'POST':
        if 'update_interview' in request.POST:
            form = InterviewUpdateForm(request.POST, instance=application)
            if form.is_valid():
                app = form.save()
                if app.interview_score is not None:
                    app.compute_final_score()
                rank_applicants_for_job(application.job)
                messages.success(request, "Application updated!")
                return redirect('application_detail_hr', pk=pk)
        elif 'add_note' in request.POST:
            note_form = InterviewNoteForm(request.POST)
            if note_form.is_valid():
                note = note_form.save(commit=False)
                note.application = application
                note.created_by = request.user
                note.save()
                messages.success(request, "Note added!")
                return redirect('application_detail_hr', pk=pk)

    form = InterviewUpdateForm(instance=application)
    note_form = InterviewNoteForm()
    notes = application.notes.all().order_by('-created_at')

    context = {
        'application': application,
        'form': form,
        'note_form': note_form,
        'notes': notes,
    }
    return render(request, 'core/application_detail_hr.html', context)


@require_hr
def process_ai(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    try:
        score = process_application(application)
        rank_applicants_for_job(application.job)
        messages.success(request, f"AI processed. Similarity score: {score:.2%}")
    except Exception as e:
        messages.error(request, f"AI processing failed: {str(e)}")
    return redirect('application_detail_hr', pk=pk)


@require_hr
def process_all_ai(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk, hr=request.user)
    applications = job.applications.all()
    errors = []
    for app in applications:
        try:
            process_application(app)
        except Exception as e:
            errors.append(str(e))
    rank_applicants_for_job(job)
    if errors:
        messages.warning(request, f"Processed with {len(errors)} errors.")
    else:
        messages.success(request, f"All {applications.count()} applications processed and ranked!")
    return redirect('job_applicants', pk=job_pk)


@require_hr
def hr_reports(request):
    jobs = Job.objects.filter(hr=request.user)
    report_data = []
    for job in jobs:
        apps = job.applications.all()
        report_data.append({
            'job': job,
            'total': apps.count(),
            'shortlisted': apps.filter(status='shortlisted').count(),
            'in_interview': apps.filter(status__in=['hr_interview', 'technical_interview', 'final_interview']).count(),
            'selected': apps.filter(status='selected').count(),
            'rejected': apps.filter(status__in=['not_shortlisted', 'rejected']).count(),
        })
    return render(request, 'core/hr_reports.html', {'report_data': report_data})


# ── Candidate Views ───────────────────────────────────────────────────────────

@require_candidate
def candidate_dashboard(request):
    applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-applied_at')
    return render(request, 'core/candidate_dashboard.html', {'applications': applications})


@require_candidate
def job_list(request):
    today = timezone.now().date()
    jobs = Job.objects.filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today),
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).select_related('hr')
    applied_job_ids = Application.objects.filter(
        candidate=request.user
    ).values_list('job_id', flat=True)
    return render(request, 'core/job_list.html', {
        'jobs': jobs,
        'applied_job_ids': list(applied_job_ids)
    })


@require_candidate
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_list')

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.status = 'applied'
            application.save()
            try:
                process_application(application)
                rank_applicants_for_job(job)
                messages.success(request, f"Application submitted! Your match score: {application.similarity_score:.2%}")
            except Exception as e:
                messages.success(request, "Application submitted! AI processing will run shortly.")
            return redirect('candidate_dashboard')
    else:
        form = ResumeUploadForm()

    return render(request, 'core/apply_job.html', {'job': job, 'form': form})


@require_candidate
def application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, candidate=request.user)
    notes = []
    if application.can_see_interview():
        notes = application.notes.all().order_by('-created_at')
    return render(request, 'core/application_status.html', {
        'application': application,
        'notes': notes,
    })