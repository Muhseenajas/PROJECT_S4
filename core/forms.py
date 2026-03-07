from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Job, Application, InterviewNote


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [('hr', 'HR / Admin'), ('candidate', 'Candidate')]
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone', '')
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        if profile:
            self.fields['phone'].initial = profile.phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.profile:
            self.profile.phone = self.cleaned_data.get('phone', '')
            self.profile.save()
        return user


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'required_skills', 'required_experience', 'description', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'Python, Django, Machine Learning'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'required_skills': 'Enter skills separated by commas',
            'start_date': 'Job posting start date',
            'end_date': 'Application deadline date',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume']

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            ext = resume.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx']:
                raise forms.ValidationError("Only PDF and DOCX files are allowed.")
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB.")
        return resume


# ── Phase 4: Shortlist Form ───────────────────────────────────────────────────

class ShortlistForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']

    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('not_shortlisted', 'Not Shortlisted'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = self.STATUS_CHOICES


# ── Phase 5: Technical Interview Forms ───────────────────────────────────────

class TechnicalScheduleForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['technical_date']
        widgets = {
            'technical_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'technical_date': 'Technical Interview Date',
        }


class TechnicalScoreForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['technical_score', 'technical_attended', 'technical_feedback']
        widgets = {
            'technical_feedback': forms.Textarea(attrs={'rows': 4,
                'placeholder': 'Enter feedback about technical interview...'}),
            'technical_score': forms.NumberInput(attrs={'min': 0, 'max': 10,
                'step': 0.1, 'placeholder': 'Score out of 10'}),
        }
        labels = {
            'technical_score': 'Technical Score (out of 10)',
            'technical_attended': 'Candidate Attended?',
            'technical_feedback': 'Technical Feedback',
        }


# ── Phase 6: HR Interview Forms ───────────────────────────────────────────────

class HRScheduleForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['hr_date']
        widgets = {
            'hr_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'hr_date': 'HR Interview Date',
        }


class HRScoreForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['hr_score', 'hr_attended', 'hr_feedback']
        widgets = {
            'hr_feedback': forms.Textarea(attrs={'rows': 4,
                'placeholder': 'Enter feedback about HR interview...'}),
            'hr_score': forms.NumberInput(attrs={'min': 0, 'max': 10,
                'step': 0.1, 'placeholder': 'Score out of 10'}),
        }
        labels = {
            'hr_score': 'HR Score (out of 10)',
            'hr_attended': 'Candidate Attended?',
            'hr_feedback': 'HR Feedback',
        }


# ── Phase 8: Final Decision Form ──────────────────────────────────────────────

class FinalDecisionForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['final_decision', 'hr_decision_notes']
        widgets = {
            'hr_decision_notes': forms.Textarea(attrs={'rows': 4,
                'placeholder': 'Enter notes for final decision...'}),
        }
        labels = {
            'final_decision': 'Final Decision',
            'hr_decision_notes': 'Decision Notes',
        }

    DECISION_CHOICES = [
        ('selected', '✅ Select Candidate'),
        ('rejected', '❌ Reject Candidate'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['final_decision'].choices = self.DECISION_CHOICES


class InterviewNoteForm(forms.ModelForm):
    class Meta:
        model = InterviewNote
        fields = ['stage', 'note', 'score']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }