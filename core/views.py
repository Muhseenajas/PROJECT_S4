from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import UserProfile, Job, Application, InterviewNote
from .forms import (
    RegisterForm, ProfileUpdateForm, JobForm,
    ResumeUploadForm, InterviewNoteForm,
    ShortlistForm, TechnicalScheduleForm, TechnicalScoreForm,
    HRScheduleForm, HRScoreForm, FinalDecisionForm
)
from .ai_engine import process_application, rank_applicants_for_job


# ── Helpers ──────────────────────────────────────────────────────────────────

def require_hr(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_hr():
            messages.error(request, "Access denied. HR only.")
            return redirect('dashboard')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def require_candidate(func):
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
    technical_attended = Application.objects.filter(
        job__hr=request.user, status__in=['technical_completed', 'hr_scheduled', 'hr_completed', 'system_recommended', 'selected', 'rejected'],
        technical_attended=True
    ).count()
    hr_attended = Application.objects.filter(
        job__hr=request.user, status__in=['hr_completed', 'system_recommended', 'selected', 'rejected'],
        hr_attended=True
    ).count()
    selected = Application.objects.filter(job__hr=request.user, status='selected').count()
    rejected = Application.objects.filter(job__hr=request.user, status__in=['not_shortlisted', 'rejected']).count()

    context = {
        'jobs': jobs,
        'total_apps': total_apps,
        'shortlisted': shortlisted,
        'technical_attended': technical_attended,
        'hr_attended': hr_attended,
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
    applications = job.applications.select_related(
        'candidate', 'candidate__profile'
    ).order_by('-resume_score')
    return render(request, 'core/job_applicants.html', {
        'job': job,
        'applications': applications
    })


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
        messages.success(request, f"All {applications.count()} applications processed!")
    return redirect('job_applicants', pk=job_pk)


# ── Phase 4: Shortlist ────────────────────────────────────────────────────────

@require_hr
def shortlist_candidate(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    if request.method == 'POST':
        form = ShortlistForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f"Status updated to: {application.get_status_display()}")
            return redirect('job_applicants', pk=application.job.pk)
    else:
        form = ShortlistForm(instance=application)
    return render(request, 'core/shortlist.html', {
        'application': application,
        'form': form
    })


# ── Phase 5: Technical Interview ─────────────────────────────────────────────

@require_hr
def schedule_technical(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    if request.method == 'POST':
        form = TechnicalScheduleForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = 'technical_scheduled'
            app.save()
            messages.success(request, f"Technical interview scheduled for {app.technical_date}")
            return redirect('job_applicants', pk=application.job.pk)
    else:
        form = TechnicalScheduleForm(instance=application)
    return render(request, 'core/schedule_technical.html', {
        'application': application,
        'form': form
    })


@require_hr
def enter_technical_score(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    if request.method == 'POST':
        form = TechnicalScoreForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = 'technical_completed'
            app.save()
            messages.success(request, "Technical interview scores saved!")
            return redirect('job_applicants', pk=application.job.pk)
    else:
        form = TechnicalScoreForm(instance=application)
    return render(request, 'core/enter_technical_score.html', {
        'application': application,
        'form': form
    })


# ── Phase 6: HR Interview ─────────────────────────────────────────────────────

@require_hr
def schedule_hr_interview(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    if request.method == 'POST':
        form = HRScheduleForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = 'hr_scheduled'
            app.save()
            messages.success(request, f"HR interview scheduled for {app.hr_date}")
            return redirect('job_applicants', pk=application.job.pk)
    else:
        form = HRScheduleForm(instance=application)
    return render(request, 'core/schedule_hr.html', {
        'application': application,
        'form': form
    })


@require_hr
def enter_hr_score(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    if request.method == 'POST':
        form = HRScoreForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = 'hr_completed'
            app.save()
            # Auto calculate final score
            app.compute_final_score()
            messages.success(request, "HR scores saved! Final score calculated.")
            return redirect('job_applicants', pk=application.job.pk)
    else:
        form = HRScoreForm(instance=application)
    return render(request, 'core/enter_hr_score.html', {
        'application': application,
        'form': form
    })


# ── Phase 8: Final Decision ───────────────────────────────────────────────────

@require_hr
def final_decision(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    if request.method == 'POST':
        form = FinalDecisionForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = app.final_decision
            app.save()
            messages.success(request, f"Final decision saved: {app.get_final_decision_display()}")
            return redirect('job_applicants', pk=application.job.pk)
    else:
        form = FinalDecisionForm(instance=application)
    return render(request, 'core/final_decision.html', {
        'application': application,
        'form': form
    })


@require_hr
def application_detail_hr(request, pk):
    application = get_object_or_404(Application, pk=pk, job__hr=request.user)
    note_form = InterviewNoteForm()
    if request.method == 'POST':
        note_form = InterviewNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.application = application
            note.created_by = request.user
            note.save()
            messages.success(request, "Note added!")
            return redirect('application_detail_hr', pk=pk)
    notes = application.notes.all().order_by('-created_at')
    return render(request, 'core/application_detail_hr.html', {
        'application': application,
        'note_form': note_form,
        'notes': notes,
    })


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
            'technical_attended': apps.filter(technical_attended=True).count(),
            'hr_attended': apps.filter(hr_attended=True).count(),
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
    return render(request, 'core/candidate_dashboard.html', {
        'applications': applications
    })


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
                score = process_application(application)
                rank_applicants_for_job(job)
                messages.success(request, f"Application submitted! Your match score: {score:.2%}")
            except Exception as e:
                messages.success(request, "Application submitted! AI processing will run shortly.")
            return redirect('candidate_dashboard')
    else:
        form = ResumeUploadForm()
    return render(request, 'core/apply_job.html', {'job': job, 'form': form})


@require_candidate
def application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, candidate=request.user)
    return render(request, 'core/application_status.html', {
        'application': application,
    })