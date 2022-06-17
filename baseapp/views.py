from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView

from .calculations.calculations import calculations_1_1, calculation2, \
    calculation_npv
from .calculations.expected_flows import calculation_expected_flows
from .forms import ProjectForm
from .models import Project
from .cruid import get_project_object, scenario_from_database, \
    climate_conditions_from_database, disaster_impacts_from_database, \
    change_disaster_impact_from_database
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
        _record.optimistic_scenario.delete()
        _record.pesimistic_scenario.delete()
        _record.delete()
    return HttpResponseRedirect(reverse('baseapp:home'))


def scenario_view(scenario_object, project_object):
    scenario = scenario_from_database(scenario_object, project_object)
    df_discounted, nvp = calculation_npv(project_object, scenario['df'].copy(),
                                         scenario['dfi'])
    return {'name': scenario['name'],
            'df_html': scenario['df'].to_html(classes='table table-stripped'),
            'df_discounted_html': df_discounted.to_html(
                classes='table table-stripped'),
            'nvp': nvp
            }


@login_required
def optimistic_scenario_view(request, project_id):
    project_object = get_project_object(project_id)
    if project_object:
        context = scenario_view(project_object.optimistic_scenario,
                                project_object)
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def pesimistic_scenario_view(request, project_id):
    project_object = get_project_object(project_id)
    if project_object:
        context = scenario_view(project_object.pesimistic_scenario,
                                project_object)
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


def climate_conditions_view(request, project_id, with_project):
    _record = get_project_object(project_id)
    if _record:
        df = climate_conditions_from_database(_record, with_project)

        context = {
            'df_html': df.to_html(classes='table table-stripped'),
            'name': 'Change in average climate conditions {} project'.format(
                'WITH' if with_project else 'WITHOUT')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def climate_conditions_with_project_view(request, project_id):
    return climate_conditions_view(request, project_id, True)


@login_required
def climate_conditions_without_project_view(request, project_id):
    return climate_conditions_view(request, project_id, False)


@login_required
def disaster_impact_view(request, project_id, disaster_impact_name):
    _record = get_project_object(project_id)
    if _record:
        df = change_disaster_impact_from_database(_record, disaster_impact_name)

        context = {'df_html': df.to_html(classes='table table-stripped')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculations1_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        cc_with_project, cc_with_project_table = calculations_1_1(_record, True)
        cc_without_project, cc_without_project_table = calculations_1_1(_record,
                                                                        False)

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


@login_required
def calculations2_view(request, project_id):
    _record = get_project_object(project_id)
    context_data = []
    if _record:
        for disaster_impact_name in disaster_impacts_from_database(project_id):
            c2_1, c2_2, c2_3 = calculation2(_record, disaster_impact_name)
            context_data.append((disaster_impact_name,
                                 c2_1.to_html(classes='table table-stripped'),
                                 c2_2.to_html(classes='table table-stripped'),
                                 c2_3.to_html(classes='table table-stripped'))
                                )
        context = {'context_data': context_data}
        return render(request, 'baseapp/calculations2.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculations3_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        context_data = []
        for rez in calculation_expected_flows(_record):
            context_data.append((rez['name'],
                                 rez['df'].to_html(
                                     classes='table table-stripped'),
                                 rez['df_discounted'].to_html(
                                     classes='table table-stripped'),
                                 rez['nvp']
                                 ))
        context = {'context_data': context_data}
        return render(request, 'baseapp/expected_folows.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def results_view(request, project_id):
    _record = get_project_object(project_id)
    if _record:
        context_data = []
        for rez in calculation_expected_flows(_record, test_mode=False):
            context_data.append((rez['name'],
                                 rez['nvp']
                                 ))
        context = {'context_data': context_data}
        return render(request, 'baseapp/results.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


class ProjectFormView(FormView):
    template_name = 'baseapp/project_view.html'
    form_class = ProjectForm
    success_url = '/'


class ProjectUpdateView(UpdateView):
    model = Project
    fields = ['name', 'start_year', 'lifetime', 'discount_rate']
    template_name_suffix = '_update_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_id = self.kwargs.get('pk', None)
        list_disaster_impacts = []
        if project_id:
            for x in disaster_impacts_from_database(project_id):
                list_disaster_impacts.append(
                    (f'disaster_impact/{x}/', x))
        max_col = len(list_disaster_impacts) if len(
            list_disaster_impacts) > 2 else 2

        table_rows = [
            {
                'name': 'Scenario',
                'data_row': [
                    ('optimistic_scenario/', 'OPTIMISTIC BASELINE SCENARIO'),
                    ('pesimistic_scenario/', 'PESIMISTIC BASELINE SCENARIO'),
                ]
            },
            {
                'name': 'Climate  impact',
                'data_row': [
                    ('climate_conditions_with_project/', 'WITH project'),
                    ('climate_conditions_without_project/', 'WITHOUT project'),
                ]
            },
            {
                'name': 'Disaster impacts',
                'data_row': list_disaster_impacts
            }
        ]

        context['table_input_data'] = self.table_view(table_rows, max_col)
        return context

    def table_view(self, table_rows, max_col):
        tablebody_list = []
        for x in table_rows:
            tablebody_row = [
                '<td><h4>{name}</h4></td>'.format(name=x['name'], ), ]
            for url, url_name in x['data_row']:
                tablebody_row.append('''
                        <td>
                            <a class="btn btn-link"
                               href="{url}">{url_name}</a>
                        </td>'''.format(url=url, url_name=url_name))
            for i in range(2, max_col):
                tablebody_row.append('<td></td>')
            tablebody_list.append("<tr> {data_line}</tr>".format(
                data_line="\n".join(tablebody_row)))
        tablebody = "\n".join(tablebody_list)

        return """<p></p>
            <p></p>
            <table class ="table table-borderless" >
               <tbody> <tr>
               {tablebody}
               </tr> </tbody>
            </table>""".format(tablebody=tablebody)
