from django import forms
from .models import UserProfile, JobApplication

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'bio', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your address'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself'
            }),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'notes']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write your cover letter here'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Add any additional notes or information'
            }),
        } 