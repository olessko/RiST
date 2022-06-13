from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    name = forms.CharField()
    start_year = forms.IntegerField()
    lifetime = forms.IntegerField()
    discount_rate = forms.FloatField()

    class Meta:
        model = Project
        fields = ['name', 'start_year', 'lifetime', 'discount_rate']
