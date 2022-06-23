from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    name = forms.CharField()
    start_year = forms.IntegerField()
    lifetime = forms.IntegerField()
    discount_rate = forms.FloatField()
    threshold_below_for_risk = forms.FloatField()
    level_of_climate_impact = forms.FloatField()
    baseline_pessimism = forms.FloatField()

    class Meta:
        model = Project
        fields = ['name', 'start_year', 'lifetime', 'discount_rate']
