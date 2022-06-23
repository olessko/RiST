from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView
from django_q.tasks import async_task

from .calculations.calculations import calculations_1_1, calculations_1_2, \
    calculation_npv, calculation2_1, calculation2_2, calculation2_3
from .calculations.expected_flows import calculation_expected_flows
from .calculations.project_object import ProjectObject
from .forms import ProjectForm
from .models import Project
from .cruid import get_project_object, disasters_from_database, \
    calculations_from_database, analysis_result_from_database
from .parsers import read_from_exel
from .tasks import calculations_task


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


def scenario_view(scenario, project_object):
    df_discounted, npv = calculation_npv(project_object, scenario['df'].copy(),
                                         scenario['dfi'])
    return {'name': scenario['name'],
            'df_html': scenario['df'].to_html(classes='table table-stripped'),
            'df_discounted_html': df_discounted.to_html(
                classes='table table-stripped'),
            'npv': npv
            }


@login_required
def optimistic_scenario_view(request, project_id):
    project_object = ProjectObject(project_id)
    if project_object:
        context = scenario_view(project_object.get_optimistic_scenario(),
                                project_object)
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def pesimistic_scenario_view(request, project_id):
    project_object = ProjectObject(project_id)
    if project_object:
        context = scenario_view(project_object.get_pesimistic_scenario(),
                                project_object)
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


def climate_conditions_view(request, project_id, with_project):
    project_object = ProjectObject(project_id)
    if project_object:
        df = project_object.get_climate_conditions(with_project=with_project)
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
def disaster_impact_view(request, project_id, disaster_name):
    project_object = ProjectObject(project_id)
    if project_object:
        df = project_object.get_disaster_impacts(disaster_name=disaster_name)
        context = {'df_html': df.to_html(classes='table table-stripped')}
        return render(request, 'baseapp/scenario.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculations1_view(request, project_id):
    project_object = ProjectObject(project_id)
    context = {}
    if project_object:
        for with_project in [True, False]:
            df = calculations_1_1(project_object, with_project)
            df_table = calculations_1_2(project_object, df.copy())
            t1 = 'with' if with_project else 'without'
            context[f'df_{t1}_project_html'] = df.to_html(
                classes='table table-stripped')
            context[f'df_{t1}_project_table_html'] = df_table.to_html(
                classes='table table-stripped')

        return render(request, 'baseapp/calculations1.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculations2_view(request, project_id):
    context_data = []
    project_object = ProjectObject(project_id)
    if project_object:
        for disaster_name in project_object.get_disasters():
            c2_1 = calculation2_1(project_object, disaster_name)
            c2_2 = calculation2_2(project_object, c2_1.copy())
            c2_3 = calculation2_3(project_object, c2_2.copy())
            context_data.append((disaster_name,
                                 c2_1.to_html(classes='table table-stripped'),
                                 c2_2.to_html(classes='table table-stripped'),
                                 c2_3.to_html(classes='table table-stripped'))
                                )
        context = {'context_data': context_data}
        return render(request, 'baseapp/calculations2.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculations3_view(request, project_id):
    project_object = ProjectObject(project_id)
    if project_object:
        context_data = []
        for rez in calculation_expected_flows(project_object):
            context_data.append((rez['type_value'],
                                 rez['df'].to_html(
                                     classes='table table-stripped'),
                                 rez['df_discounted'].to_html(
                                     classes='table table-stripped'),
                                 rez['value']
                                 ))
        context = {'context_data': context_data}
        return render(request, 'baseapp/expected_folows.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def results_view(request, project_id):
    project_object = ProjectObject(project_id)
    if project_object:
        rows = [['Threshold below which risk is unaccetable (NPV)', 0],
                ['Climate change impact (0%=no/low impact, 100%=high impact)',
                 100],
                ['Baseline scenario (0%=optimistic, 100%=pessimistic)', 0]]
        table_parameters = table_view('PARAMETERS OF THE ANALYSIS', rows)

        rows = []
        for rez in analysis_result_from_database(project_object, 'base'):
            rows.append([rez['type_value'], rez['value']])
        table_npv = table_view('NPV (USD, millions)', rows)

        c_for_graph = calculations_from_database(project_object)

        context = {'table_npv': table_npv,
                   'table_parameters': table_parameters,
                   'table_calculations_for_graph':
                       c_for_graph.to_html(
                           classes='table table-stripped')}
        return render(request, 'baseapp/results.html', context)
    return HttpResponseRedirect(reverse('baseapp:home'))


@login_required
def calculate_view(request, project_id):
    project_object = ProjectObject(project_id)
    if project_object:
        opts = {'timeout': 600}
        async_task(calculations_task, project_id, q_options=opts)
        return results_view(request, project_id)
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
            for x in disasters_from_database(project_id):
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


def table_view(name, rows, header=None):
    tablebody = "  <p></p>\n  <tr>\n"
    if header:
        for column in header:
            tablebody += f"    <th>{column}</th>\n"
        tablebody += "  </tr>\n"

    for row in rows:
        tablebody += "  <tr>\n"
        for column in row:
            tablebody += f"    <td>{column}</td>\n"
        tablebody += "  </tr>\n"

    return f"""<p></p>
            <h5>{name}</h5>
            <table border=1 class ="table table" >
               <tbody> <tr>
               {tablebody}
               </tr> </tbody>
            </table>"""
