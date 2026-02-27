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


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'required_skills', 'required_experience', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'Python, Django, Machine Learning'}),
        }
        help_texts = {
            'required_skills': 'Enter skills separated by commas',
        }


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


class InterviewUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'interview_date', 'interview_score', 'hr_notes']
        widgets = {
            'interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'hr_notes': forms.Textarea(attrs={'rows': 4}),
        }

    STATUS_CHOICES_HR = [
        ('shortlisted', 'Shortlisted'),
        ('hr_interview', 'HR Interview'),
        ('technical_interview', 'Technical Interview'),
        ('final_interview', 'Final Interview'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = self.STATUS_CHOICES_HR


class InterviewNoteForm(forms.ModelForm):
    class Meta:
        model = InterviewNote
        fields = ['stage', 'note', 'score']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
