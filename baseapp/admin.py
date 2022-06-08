from django.contrib import admin

from .models import Project, ProjectInvestmentCost, Scenario, \
    InvestmentTypeValue, ScenarioData, ScenarioInvestmentData, \
    DisasterImpact, LevelDisasterImpact, ClimateImpactsTypeValue, \
    ChangeClimateCondition, ChangeDisasterImpact, SensitivityAnalysis


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_year', 'lifetime', 'id')


admin.site.register(Project, ProjectAdmin)


class ProjectInvestmentCostAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'id')


admin.site.register(ProjectInvestmentCost, ProjectInvestmentCostAdmin)


class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(Scenario, ScenarioAdmin)


class InvestmentTypeValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(InvestmentTypeValue, InvestmentTypeValueAdmin)


class ScenarioDataAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'cost', 'with_project',
                    'type_value', 'year', 'value', 'id')


admin.site.register(ScenarioData, ScenarioDataAdmin)


class ScenarioInvestmentDataAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'year', 'value', 'id')


admin.site.register(ScenarioInvestmentData, ScenarioInvestmentDataAdmin)


class DisasterImpactAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(DisasterImpact, DisasterImpactAdmin)


class LevelDisasterImpactAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(LevelDisasterImpact, LevelDisasterImpactAdmin)


class ClimateImpactsTypeValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'id')


admin.site.register(ClimateImpactsTypeValue, ClimateImpactsTypeValueAdmin)


class ChangeClimateConditionAdmin(admin.ModelAdmin):
    list_display = ('type_value', 'cost', 'with_project', 'impact',
                    'year', 'value', 'id')


admin.site.register(ChangeClimateCondition, ChangeClimateConditionAdmin)


class ChangeDisasterImpactAdmin(admin.ModelAdmin):
    list_display = ('type_value', 'disaster_impact', 'level_disaster_impact',
                    'impact', 'year', 'return_period', 'id')


admin.site.register(ChangeDisasterImpact, ChangeDisasterImpactAdmin)


class SensitivityAnalysisAdmin(admin.ModelAdmin):
    list_display = ('name', 'disaster_impact_name', 'section',
                    'value', 'project', 'id')


admin.site.register(SensitivityAnalysis, SensitivityAnalysisAdmin)
