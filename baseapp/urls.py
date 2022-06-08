from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import ProjectView, upload_project, delete_project_view, \
    ProjectFormView, optimistic_scenario_view, \
    pesimistic_scenario_view, climate_conditions_without_project_view, \
    climate_conditions_with_project_view, calculations1_view

app_name = 'baseapp'

urlpatterns = [

    path('', login_required(ProjectView.as_view()), name='home'),
    path('load_project/', upload_project, name='load_project'),
    path(r'delete_project/<project_id>/', delete_project_view,
         name='delete_project'),
    path(r'optimistic_scenario/<project_id>/', optimistic_scenario_view,
         name='scenario_view'),
    path(r'pesimistic_scenario/<project_id>/', pesimistic_scenario_view,
         name='scenario_view'),
    path('project/<int:pk>/', login_required(ProjectFormView.as_view()),
         name='project_view'),

    path(r'climate_conditions_with_project/<project_id>/',
         climate_conditions_with_project_view,
         name='climate_conditions_wit_project_view'),
    path(r'climate_conditions_without_project/<project_id>/',
         climate_conditions_without_project_view,
         name='climate_conditions_without_project_view'),

    path(r'calculations1/<project_id>/',
         calculations1_view,
         name='calculations1_view'),

]
