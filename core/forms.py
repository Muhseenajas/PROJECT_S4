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
    phone = forms.CharField(
        max_length=10,
        min_length=10,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10 digit phone number'}),
        error_messages={
            'min_length': 'Phone number must be exactly 10 digits.',
            'max_length': 'Phone number must be exactly 10 digits.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError("Phone number must contain digits only.")
            if len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

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
    phone = forms.CharField(
        max_length=10,
        min_length=10,
        required=False,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10 digit phone number'}),
        error_messages={
            'min_length': 'Phone number must be exactly 10 digits.',
            'max_length': 'Phone number must be exactly 10 digits.',
        }
    )
    profile_image = forms.ImageField(
        required=False,
        label="Profile Picture",
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        if profile:
            self.fields['phone'].initial = profile.phone
            self.fields['profile_image'].initial = profile.profile_image

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError("Phone number must contain digits only.")
            if len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Check file size max 2MB
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image size must be under 2MB.")
            # Check file type
            ext = image.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                raise forms.ValidationError("Only JPG, PNG and GIF images are allowed.")
        return image

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.profile:
            self.profile.phone = self.cleaned_data.get('phone', '')
            # Only update image if a new one was uploaded
            image = self.cleaned_data.get('profile_image')
            if image:
                self.profile.profile_image = image
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


# ── Phase 4: Shortlist Form ──────────────────────────────────────

class ShortlistForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('not_shortlisted', 'Not Shortlisted'),
    ]

    class Meta:
        model = Application
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = self.STATUS_CHOICES


# ── Phase 5: Technical Interview Forms ──────────────────────────

class TechnicalScheduleForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['technical_date', 'technical_time', 'technical_interviewer']
        widgets = {
            'technical_date': forms.DateInput(attrs={'type': 'date'}),
            'technical_time': forms.TimeInput(attrs={'type': 'time'}),
            'technical_interviewer': forms.TextInput(attrs={
                'placeholder': 'Enter interviewer name'
            }),
        }
        labels = {
            'technical_date': 'Technical Interview Date',
            'technical_time': 'Technical Interview Time',
            'technical_interviewer': 'Interviewer Name',
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('technical_date')
        time = cleaned_data.get('technical_time')
        if not date:
            raise forms.ValidationError("Interview date is required.")
        if not time:
            raise forms.ValidationError("Interview time is required.")
        return cleaned_data


class TechnicalScoreForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['technical_score', 'technical_attended', 'technical_feedback']
        widgets = {
            'technical_feedback': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter feedback about technical interview...'
            }),
            'technical_score': forms.NumberInput(attrs={
                'min': 0, 'max': 10, 'step': 0.1,
                'placeholder': 'Score out of 10'
            }),
        }
        labels = {
            'technical_score': 'Technical Score (out of 10)',
            'technical_attended': 'Candidate Attended?',
            'technical_feedback': 'Technical Feedback',
        }


# ── Phase 6: HR Interview Forms ─────────────────────────────────

class HRScheduleForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['hr_date', 'hr_time', 'hr_interviewer']
        widgets = {
            'hr_date': forms.DateInput(attrs={'type': 'date'}),
            'hr_time': forms.TimeInput(attrs={'type': 'time'}),
            'hr_interviewer': forms.TextInput(attrs={
                'placeholder': 'Enter interviewer name'
            }),
        }
        labels = {
            'hr_date': 'HR Interview Date',
            'hr_time': 'HR Interview Time',
            'hr_interviewer': 'Interviewer Name',
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('hr_date')
        time = cleaned_data.get('hr_time')
        if not date:
            raise forms.ValidationError("Interview date is required.")
        if not time:
            raise forms.ValidationError("Interview time is required.")
        return cleaned_data


class HRScoreForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['hr_score', 'hr_attended', 'hr_feedback']
        widgets = {
            'hr_feedback': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter feedback about HR interview...'
            }),
            'hr_score': forms.NumberInput(attrs={
                'min': 0, 'max': 10, 'step': 0.1,
                'placeholder': 'Score out of 10'
            }),
        }
        labels = {
            'hr_score': 'HR Score (out of 10)',
            'hr_attended': 'Candidate Attended?',
            'hr_feedback': 'HR Feedback',
        }


# ── Phase 8: Final Decision Form ────────────────────────────────

class FinalDecisionForm(forms.ModelForm):
    DECISION_CHOICES = [
        ('selected', '✅ Select Candidate'),
        ('rejected', '❌ Reject Candidate'),
    ]

    class Meta:
        model = Application
        fields = ['final_decision', 'hr_decision_notes']
        widgets = {
            'hr_decision_notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter notes for final decision...'
            }),
        }
        labels = {
            'final_decision': 'Final Decision',
            'hr_decision_notes': 'Decision Notes',
        }

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