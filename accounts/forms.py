from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='user name')
    password = forms.CharField(label='password ', widget=forms.PasswordInput)
