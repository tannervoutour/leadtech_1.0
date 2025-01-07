from django import forms
from .models import Log

class LogForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = ['machine', 'log_text']
        widgets = {
            'machine': forms.TextInput(attrs={'placeholder': 'Enter machine/workspace name'}),
            'log_text': forms.Textarea(attrs={'placeholder': 'Enter your log details'}),
        }
