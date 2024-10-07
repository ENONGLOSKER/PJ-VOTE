# voting/forms.py
from django import forms
from .models import Vote, Option

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['title', 'description', 'key', 'deadline']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_text']

class VoteAccessForm(forms.Form):
    key = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'style': 'padding: 12px 14px; font-weight: 600; text-align: center; font-size: 20px; border-radius: 12px; border: none; box-shadow: 2px 2px 30px #7FFA8A; width: 100%;',
            'placeholder': 'Masukan Kunci!'
        })
    )