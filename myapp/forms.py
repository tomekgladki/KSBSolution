from django import forms
from .models import UserPreferences
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['lista_krajów', 'sektory', 'kryterium']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    # Add custom validation messages for email and username fields
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    username = forms.CharField(
        max_length=150,
        error_messages={
            'required': 'Username is required.',
            'max_length': 'Username must be 150 characters or fewer.'
        }
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        error_messages={
            'required': 'Password is required.'
        }
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        error_messages={
            'required': 'Password confirmation is required.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Optional: Add custom title to inputs for user hints
        self.fields['username'].widget.attrs['title'] = 'Username (max 150 characters, letters, digits, @/./+/-/_ only)'
        self.fields['email'].widget.attrs['title'] = 'Enter a valid email address'
        self.fields['password1'].widget.attrs['title'] = 'Password must be at least 8 characters'
        self.fields['password2'].widget.attrs['title'] = 'Confirm your password'
