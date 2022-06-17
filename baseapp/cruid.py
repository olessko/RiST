import pandas as pd

from .models import Project, ProjectInvestmentCost, Scenario, \
    InvestmentTypeValue, ScenarioData, ScenarioInvestmentData, \
    DisasterImpact, LevelDisasterImpact, ClimateImpactsTypeValue, \
    ChangeClimateCondition, ChangeDisasterImpact, SensitivityAnalysis, \
    ProjectsDisasterImpact


def get_project(name: str):
    return Project.objects.filter(name=name).first()


def get_project_object(_id: int):
    return Project.objects.filter(pk=_id).first()


def get_project_investment_cost(name, project_object):
    _data = ProjectInvestmentCost.objects.filter(
        name=name, project_id=project_object.id).first()
    if _data is None:
        _data = ProjectInvestmentCost(name=name, project=project_object)
        _data.save()
    return _data


def get_climate_type_values(name, section):
    _data = ClimateImpactsTypeValue.objects.filter(
        name=name, section=section).first()
    if _data is None:
        _data = ClimateImpactsTypeValue(name=name, section=section)
        _data.save()
    return _data


def get_investment_type_values(name):
    _data = InvestmentTypeValue.objects.filter(name=name).first()
    if _data is None:
        _data = InvestmentTypeValue(name=name)
        _data.save()
    return _data


def get_level_disaster_impact(name):
    _data = LevelDisasterImpact.objects.filter(name=name).first()
    if _data is None:
        _data = LevelDisasterImpact(name=name)
        _data.save()
    return _data


def get_disaster_impact(name):
    _data = DisasterImpact.objects.filter(name=name).first()
    if _data is None:
        _data = DisasterImpact(name=name)
        _data.save()
    return _data


def to_database(project_data):
    project_object = project_data['name']
    if project_object:
        project_object = Project()

        rec_scenario = Scenario()
        rec_scenario.name = 'OPTIMISTIC BASELINE SCENARIO'
        rec_scenario.save()
        project_object.optimistic_scenario = rec_scenario

        rec_scenario = Scenario()
        rec_scenario.name = 'PESIMISTIC BASELINE SCENARIO'
        rec_scenario.save()
        project_object.pesimistic_scenario = rec_scenario

    project_object.name = project_data['name']
    project_object.start_year = project_data['start_year']
    project_object.lifetime = project_data['lifetime']
    project_object.discount_rate = project_data['discount_rate']
    project_object.save()

    scenario_to_database(project_data['optimistic_scenario'],
                         project_object.optimistic_scenario, project_object)
    scenario_to_database(project_data['pesimistic_scenario'],
                         project_object.pesimistic_scenario, project_object)

    climate_conditions_to_database(project_data['data_climate_condition'],
                                   project_object)

    change_disaster_impact_to_database(
        project_data['data_change_disaster_impact'], project_object)

    climat_parameters_to_database(project_data, project_object)

    sensitivity_analysis_to_database(project_data['sensitivity_analysis'],
                                     project_object)


def scenario_to_database(scenario_data, scenario_object, project_object):
    df = scenario_data['df']

    cost_dict = {}
    unit_dict = {}

    for x in df.T.to_dict().values():
        cost, with_project, unit, *list_values = x.items()
        cost, with_project, unit = cost[1], with_project[1], unit[1]

        cost_data = cost_dict.get(cost, None)
        if cost_data is None:
            cost_dict[cost] = get_project_investment_cost(cost, project_object)
            cost_data = cost_dict[cost]

        unit_data = unit_dict.get(unit, None)
        if unit_data is None:
            unit_dict[unit] = get_investment_type_values(unit)
            unit_data = unit_dict[unit]

        for data_year in list_values:
            rec = ScenarioData(scenario=scenario_object,
                               cost=cost_data,
                               with_project=with_project,
                               type_value=unit_data,
                               year=data_year[0],
                               value=data_year[1])
            rec.save()

    list_investment_costs = scenario_data['investment_costs']
    for x in list_investment_costs:
        rec = ScenarioInvestmentData(
            scenario=scenario_object,
            year=x['year'],
            value=x['value'])
        rec.save()


def scenario_from_database(scenario_object, project_object):
    cost_data = ProjectInvestmentCost.objects.filter(
        project_id=project_object.id).order_by('id')
    unit_data = InvestmentTypeValue.objects.order_by('id')
    df_dict = {}
    num = 0
    for cost in cost_data:
        for with_project in [True, False]:
            for unit in unit_data:
                data = ScenarioData.objects.filter(
                    scenario_id=scenario_object.id,
                    cost=cost,
                    with_project=with_project,
                    type_value=unit).order_by('year')
                if data:
                    line_dict = {'cost': cost.name,
                                 'with_project': with_project,
                                 'type_value': unit.name}
                    for data_line in data:
                        line_dict[data_line.year] = data_line.value
                    df_dict[num] = line_dict
                    num += 1

    df = pd.DataFrame(df_dict)

    dfi = {}
    data = ScenarioInvestmentData.objects.filter(
        scenario_id=scenario_object.id).order_by('year')
    if data:
        for data_line in data:
            dfi[data_line.year] = data_line.value

    return {'df': df.T, 'dfi': dfi, 'name': scenario_object.name}


def climat_parameters_to_database(project_data, project_object):
    for x in project_data['disaster_impacts']:
        disaster_impact = get_disaster_impact(x)
        _data = ProjectsDisasterImpact(disaster_impact=disaster_impact,
                                       project=project_object)
        _data.save()

    for x in project_data['level_disaster_impacts']:
        get_level_disaster_impact(x)

    for x in project_data['climate_impacts_type_value']:
        get_climate_type_values(x['name'], x['section'])


def disaster_impacts_from_database(project_id):
    list_di = ProjectsDisasterImpact.objects.filter(
        project_id=project_id).order_by('id')
    return [x.disaster_impact.name for x in list_di]


def climate_conditions_to_database(data_climate_condition, project_object):
    cost_dict = {}
    type_value_dict = {}

    for x in data_climate_condition:
        cost = x.get('cost', None)
        cost = cost if cost else 'None'
        cost_data = cost_dict.get(cost, None)
        if cost_data is None:
            cost_dict[cost] = get_project_investment_cost(
                cost, project_object)
            cost_data = cost_dict[cost]

        type_value = x.get('type_value', None)
        type_value = type_value if type_value else 'None'
        type_value_data = type_value_dict.get(type_value, None)
        if type_value_data is None:
            type_value_dict[type_value] = get_climate_type_values(
                type_value, 'climate_conditions')
            type_value_data = type_value_dict[type_value]

        rec = ChangeClimateCondition(project=project_object,
                                     type_value=type_value_data,
                                     cost=cost_data,
                                     with_project=x.get('with_project', False),
                                     impact=x.get('impact', False),
                                     year=x.get('year', 0),
                                     value=x.get('value', 0))
        rec.save()


def climate_conditions_from_database(project_object, with_project):
    cost_data = ProjectInvestmentCost.objects.filter(
        project_id=project_object.id).order_by('id')
    unit_data = ClimateImpactsTypeValue.objects.filter(
        section='climate_conditions').order_by('id')
    df_dict = {}
    num = 0
    for unit in unit_data:
        for cost in cost_data:
            for impact in [False, True]:
                data = ChangeClimateCondition.objects.filter(
                    project_id=project_object.id,
                    cost=cost,
                    impact=impact,
                    with_project=with_project,
                    type_value=unit).order_by('year')
                if data:
                    line_dict = {'type_value': unit.name,
                                 'cost': cost.name,
                                 'impact': impact}
                    for data_line in data:
                        line_dict[data_line.year] = data_line.value
                    df_dict[num] = line_dict
                    num += 1

    df = pd.DataFrame(df_dict)
    return df.T


def change_disaster_impact_to_database(data_change_disaster_impact,
                                       project_object):
    disaster_impact_dict = {}
    level_disaster_impact_dict = {}
    type_value_dict = {}

    for x in data_change_disaster_impact:
        _data = x.get('disaster_impact', None)
        _data = _data if _data else 'None'
        disaster_impact_data = disaster_impact_dict.get(_data, None)
        if disaster_impact_data is None:
            disaster_impact_dict[_data] = get_disaster_impact(_data)
            disaster_impact_data = disaster_impact_dict[_data]

        _data = x.get('level_disaster_impact', None)
        _data = _data if _data else 'None'
        level_disaster_impact_data = level_disaster_impact_dict.get(_data, None)
        if level_disaster_impact_data is None:
            level_disaster_impact_dict[_data] = get_level_disaster_impact(_data)
            level_disaster_impact_data = level_disaster_impact_dict[_data]

        type_value = x.get('type_value', None)
        type_value = type_value if type_value else 'None'
        type_value_data = type_value_dict.get(type_value, None)
        if type_value_data is None:
            type_value_dict[type_value] = get_climate_type_values(
                type_value, 'disaster')
            type_value_data = type_value_dict[type_value]

        value = x.get('value', 0)
        rec = ChangeDisasterImpact(
            project=project_object,
            type_value=type_value_data,
            disaster_impact=disaster_impact_data,
            level_disaster_impact=level_disaster_impact_data,
            impact=x.get('impact', False),
            year=x.get('year', 0),
            value=0 if value is None else value)
        rec.save()


def change_disaster_impact_from_database(project_object, disaster_impact):
    level_data = LevelDisasterImpact.objects.all().order_by('id')
    unit_data = ClimateImpactsTypeValue.objects.filter(
        section='disaster').order_by('id')
    df_dict = {}
    num = 0
    for level in level_data:
        for unit in unit_data:
            for impact in [False, True]:
                data = ChangeDisasterImpact.objects.filter(
                    project_id=project_object.id,
                    disaster_impact__name=disaster_impact,
                    level_disaster_impact=level,
                    impact=impact,
                    type_value=unit).order_by('year')
                if data:
                    line_dict = {'level': level.name,
                                 'level_id': level.id,
                                 'type_value': unit.name,
                                 'impact': impact}
                    for data_line in data:
                        line_dict[data_line.year] = data_line.value
                    df_dict[num] = line_dict
                    num += 1

    df = pd.DataFrame(df_dict)
    return df.T


def sensitivity_analysis_to_database(_data, project_object):
    for x in _data:
        rec = SensitivityAnalysis(
            project=project_object,
            name=x.get('name', ''),
            disaster_impact_name=x.get('disaster_impact_name', ''),
            section=x.get('section', ''),
            value=x.get('value', 0))
        rec.save()


def sensitivity_analysis_from_database(project_object, section, disaster=None):
    unit_data = list(ClimateImpactsTypeValue.objects.filter(
        section=section).order_by('id'))
    data_dict = {}
    if section == 'disaster':
        _data = list(SensitivityAnalysis.objects.filter(
            project_id=project_object.id, section=section,
            disaster_impact_name=disaster).order_by('id'))
        for sa in _data:
            if sa.name.strip() == 'Future change in extreme event frequency (0 - 100%)':
                data_dict['year'] = sa.value
            else:
                data_dict['value'] = sa.value
    else:
        _data = list(SensitivityAnalysis.objects.filter(
            project_id=project_object.id, section=section).order_by('id'))

        for i in range(len(_data)):
            data_dict[unit_data[i].name] = _data[i].value

    return data_dict
