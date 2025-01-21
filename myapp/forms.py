from django import forms
from .models import UserPreferences
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['lista_krajów', 'sektory', 'kryterium']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']