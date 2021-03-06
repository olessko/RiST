from django.db import models
from django.urls import reverse


class Project(models.Model):
    name = models.CharField('name', blank=True, max_length=200)
    start_year = models.IntegerField('start year', blank=True, default=0)
    lifetime = models.IntegerField('lifetime', blank=True, default=0)
    discount_rate = models.DecimalField(
        'discount rate',
        max_digits=7, decimal_places=1, blank=True, default=0)
    threshold_below_for_risk = models.DecimalField(
        'Threshold below which risk is unaccetable (NPV)',
        max_digits=7, decimal_places=1, blank=True, default=0)
    level_of_climate_impact = models.DecimalField(
        'Climate change impact (0%=no/low impact, 100%=high impact)',
        max_digits=7, decimal_places=1, blank=True, default=0)
    baseline_pessimism = models.DecimalField(
        'Baseline scenario (0%=optimistic, 100%=pessimistic)',
        max_digits=7, decimal_places=1, blank=True, default=0)

    calculated = models.BooleanField(default=False)
    is_calculate = models.BooleanField(default=False)

    optimistic_scenario = models.OneToOneField(
        'Scenario',
        on_delete=models.CASCADE, related_name='optimistic_scenario')
    pesimistic_scenario = models.OneToOneField(
        'Scenario',
        on_delete=models.CASCADE, related_name='pesimistic_scenario')

    def __str__(self):
        return f"""Project: {self.name}, 
        start year: {self.start_year}, 
        lifetime:{self.lifetime}"""

    def get_absolute_url(self):
        return reverse('baseapp:project_view', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('-start_year',)


class ProjectInvestmentCost(models.Model):
    name = models.CharField('name', blank=True, max_length=50)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)


class Scenario(models.Model):
    name = models.CharField('name', blank=True, max_length=200)


class InvestmentTypeValue(models.Model):
    name = models.CharField('name', blank=True, max_length=50)


class ScenarioData(models.Model):
    scenario = models.ForeignKey('Scenario', on_delete=models.CASCADE)
    cost = models.ForeignKey('ProjectInvestmentCost',
                             on_delete=models.CASCADE)
    with_project = models.BooleanField(default=False)
    type_value = models.ForeignKey('InvestmentTypeValue',
                                   on_delete=models.CASCADE)
    year = models.IntegerField('year', blank=True, default=0)
    value = models.DecimalField('value', max_digits=15, decimal_places=2,
                                blank=True, default=0)


class ScenarioInvestmentData(models.Model):
    scenario = models.ForeignKey('Scenario', on_delete=models.CASCADE)
    year = models.IntegerField('year', blank=True, default=0)
    value = models.DecimalField('value', max_digits=15, decimal_places=2,
                                blank=True, default=0)


class DisasterImpact(models.Model):
    name = models.CharField('name', blank=True, max_length=50)


class ProjectsDisasterImpact(models.Model):
    disaster_impact = models.ForeignKey('DisasterImpact',
                                        on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)


class LevelDisasterImpact(models.Model):
    name = models.CharField('name', blank=True, max_length=50)


class ClimateImpactsTypeValue(models.Model):
    name = models.CharField('name', blank=True, max_length=80)
    section = models.CharField('section', blank=True, max_length=20)


class ChangeClimateCondition(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    type_value = models.ForeignKey('ClimateImpactsTypeValue',
                                   on_delete=models.CASCADE)
    cost = models.ForeignKey('ProjectInvestmentCost',
                             on_delete=models.CASCADE)
    with_project = models.BooleanField(default=False)
    impact = models.BooleanField(default=False)
    year = models.IntegerField('year', blank=True, default=0)
    value = models.DecimalField('value', max_digits=7, decimal_places=2,
                                blank=True, default=0)


class ChangeDisasterImpact(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    type_value = models.ForeignKey('ClimateImpactsTypeValue',
                                   on_delete=models.CASCADE)
    disaster_impact = models.ForeignKey('DisasterImpact',
                                        on_delete=models.CASCADE)
    level_disaster_impact = models.ForeignKey('LevelDisasterImpact',
                                              on_delete=models.CASCADE)
    impact = models.BooleanField(default=False)
    year = models.IntegerField('year', blank=True, default=0)
    value = models.DecimalField('value', max_digits=7, decimal_places=2,
                                blank=True, default=0)


class SensitivityAnalysis(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    name = models.CharField('name', blank=True, max_length=100)
    disaster_impact_name = models.CharField('disaster impact', blank=True,
                                            max_length=50)
    section = models.CharField('section', blank=True, max_length=20)
    value = models.DecimalField('value', max_digits=7, decimal_places=2,
                                blank=True, default=0)


class AnalysisResult(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    section = models.CharField('section', blank=True, max_length=20)
    type_value = models.CharField('type_value', blank=True, max_length=150)
    level = models.IntegerField('level', blank=True, default=0)
    value = models.DecimalField('value', max_digits=15, decimal_places=1,
                                blank=True, default=0)


class CalculationForGraph(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    baseline_pessimism = models.IntegerField('baseline pessimism', blank=True,
                                             default=0)
    level_of_climate_impact = models.IntegerField('level of climate impact',
                                                  blank=True, default=0)
    value = models.DecimalField('value', max_digits=15, decimal_places=1,
                                blank=True, default=0)
