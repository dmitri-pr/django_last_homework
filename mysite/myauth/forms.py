from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class MyUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'avatar']


class ProfileCreateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']