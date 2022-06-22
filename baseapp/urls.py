from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import ProjectView, upload_project, delete_project_view, \
    optimistic_scenario_view, pesimistic_scenario_view, \
    climate_conditions_without_project_view, \
    climate_conditions_with_project_view, calculations1_view, ProjectUpdateView, \
    disaster_impact_view, calculations2_view, calculations3_view, results_view, \
    calculate_view

app_name = 'baseapp'

urlpatterns = [

    path('', login_required(ProjectView.as_view()), name='home'),
    path('load_project/', upload_project, name='load_project'),

    path(r'project_delete/<project_id>/', delete_project_view,
         name='delete_project'),

    path('project_view/<int:pk>/', login_required(ProjectUpdateView.as_view()),
         name='project_view'),

    path('project_view/<project_id>/optimistic_scenario/',
         optimistic_scenario_view, name='optimistic_scenario_view'),

    path(r'project_view/<project_id>/pesimistic_scenario/',
         pesimistic_scenario_view, name='pesimistic_scenario_view'),

    path(r'project_view/<project_id>/climate_conditions_with_project/',
         climate_conditions_with_project_view,
         name='climate_conditions_with_project_view'),

    path(r'project_view/<project_id>/climate_conditions_without_project/',
         climate_conditions_without_project_view,
         name='climate_conditions_without_project_view'),

    path(r'project_view/<project_id>/disaster_impact/<disaster_name>/',
         disaster_impact_view,
         name='disaster_impact_view'),

    path(r'calculations1/<project_id>/', calculations1_view,
         name='calculations1'),

    path(r'calculations2/<project_id>/', calculations2_view,
         name='calculations2'),

    path(r'calculations3/<project_id>/', calculations3_view,
         name='calculations3'),

    path(r'results/<project_id>/', results_view,
         name='results'),

    path(r'calculate/<project_id>/', calculate_view,
         name='calculate'),

]
