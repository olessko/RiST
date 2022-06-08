from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView

from .calculations.calculations_1 import calculations_1_1
from .forms import ProjectForm
from .models import Project
from .cruid import get_project_object, scenario_from_database, \
    climate_conditions_from_database
from .parsers import read_from_exel


class ProjectView(ListView):
    model = Project
    template_name = 'baseapp/home.html'
    context_object_name = 'table_list'
    success_url = '/'


@login_required
def upload_project(request):
    if request.method == 'POST':
        project_file = request.FILES.get('project_file', None)
        if project_file:
            from io import BytesIO
            list_name = project_file.name.split()
            project_name = list_name[1] if len(list_name) > 1 else list_name[0]
            project_name = project_name.strip().split('.')[0]
            read_from_exel(filename=BytesIO(project_file.read()),
                           project_name=project_name)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def delete_project_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        _record.delete()
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def optimistic_scenario_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        df = scenario_from_database(_record.optimistic_scenario, _record)

        context = {'df_html': df.to_html(classes='table table-stripped')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def pesimistic_scenario_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        df = scenario_from_database(_record.pesimistic_scenario, _record)

        context = {'df_html': df.to_html(classes='table table-stripped')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def climate_conditions_with_project_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        df = climate_conditions_from_database(_record, True)

        context = {'df_html': df.to_html(classes='table table-stripped')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def climate_conditions_without_project_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        df = climate_conditions_from_database(_record, False)

        context = {'df_html': df.to_html(classes='table table-stripped')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculations1_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        cc_with_project, cc_with_project_table = calculations_1_1(_record, True)
        cc_without_project, cc_without_project_table = calculations_1_1(_record, False)

        context = {
            'climate_conditions_with_project_html':
                cc_with_project.to_html(classes='table table-stripped'),
            'climate_conditions_without_project_html':
                cc_without_project.to_html(classes='table table-stripped'),
            'climate_conditions_with_project_table_html':
                cc_with_project_table.to_html(classes='table table-stripped'),
            'climate_conditions_without_project_table_html':
                cc_without_project_table.to_html(classes='table table-stripped')
        }
        return render(request, 'baseapp/calculations1.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


class ProjectFormView(FormView):
    template_name = 'baseapp/project_view.html'
    form_class = ProjectForm
    success_url = '/'
