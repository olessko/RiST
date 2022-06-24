from decimal import Decimal

from . import SA_CROSS_TABLE
from .project_object import ProjectObject
from .calculations import calculation2, calculations_1_1, \
    calculations_1_2, calculation_npv
from .time_contoller import time_controller

v1 = 'Expected change in quantity produced (%)'
v2 = 'Expected change in price (%)'
v3 = 'Expected change in input and operational costs (%)'
v4 = 'Expected change in labor costs (%)'

t1 = 'Time Savings (USD)'
t2 = 'O&M (USD)'
t3 = 'VOC'

crosstable_vt = {v1: t1, v2: t1, v3: t2, v4: t3}
INDEX_DF = ['cost', 'with_project', 'type_value']


def to_prepare_result(project_object: ProjectObject, df, test_mode=True):
    for year in project_object.years():
        df[year] = df[year].map(lambda x: x.quantize(Decimal('1.00')))
    if test_mode:
        df = df.set_index(INDEX_DF)
        df = df.sort_index(level=INDEX_DF, sort_remaining=True)
        df = df.reset_index()
    return df


@time_controller
def flows1(project_object: ProjectObject, test_mode=True):
    """Baseline (including project pessimism but without climate impacts)"""

    baseline_pessimism = Decimal(project_object.sa.baseline_pessimism)

    optimistic_scenario = project_object.get_optimistic_scenario()
    df_optimistic_scenario = optimistic_scenario['df'].copy()
    dfi_optimistic_scenario = optimistic_scenario['dfi']

    pesimistic_scenario = project_object.get_pesimistic_scenario()
    df_pesimistic_scenario = pesimistic_scenario['df'].copy()
    dfi_pesimistic_scenario = pesimistic_scenario['dfi']

    dfi = {}
    for year in project_object.years():
        dfi[year] = dfi_pesimistic_scenario[year] * baseline_pessimism + \
                    dfi_optimistic_scenario[year] * (1 - baseline_pessimism)
        df_optimistic_scenario[year] = df_optimistic_scenario[year].map(
            lambda x: x * (1 - baseline_pessimism))
        df_pesimistic_scenario[year] = df_pesimistic_scenario[year].map(
            lambda x: x * baseline_pessimism)

    df = df_optimistic_scenario.append(df_pesimistic_scenario)
    df = df.groupby(by=INDEX_DF, as_index=False).sum()
    df = to_prepare_result(project_object, df, test_mode)
    return df, dfi


def flows2i(project_object: ProjectObject, df_ef1, with_project):
    df = calculations_1_1(project_object, with_project)
    df = calculations_1_2(project_object, df)
    df['with_project'] = with_project

    for year in project_object.years():
        df[year] = df[year].map(lambda x: 1 + x)
    df['type_value'] = df['type_value'].map(
        lambda x: crosstable_vt.get(x, None))

    df1 = df.query('type_value == @t1').append(
        df_ef1.query('type_value == @t1 & with_project == @with_project'))
    df1 = df1.groupby(by=INDEX_DF, as_index=False).prod()

    df2 = df_ef1.query(
        'type_value != @t1 & with_project == @with_project')

    df_k2 = df.query('type_value == @t2')
    df_k3 = df.query('type_value == @t3')

    for year in project_object.years():
        k = {t2: df_k2[year].values[0],
             t3: df_k3[year].values[0]}
        df2[year] = df2[year] * df2['type_value'].map(k)

    return df1.append(df2)


@time_controller
def flows2(project_object: ProjectObject, df_ef1, test_mode=True):
    """Impacts from changes in average climate"""
    df = flows2i(project_object, df_ef1.copy(), True)
    df = df.append(flows2i(project_object, df_ef1.copy(), False))
    df = to_prepare_result(project_object, df, test_mode)
    return df


@time_controller
def flows3(project_object: ProjectObject, disasters, df, dfi, test_mode=True):
    """Impacts from changes in average climate + disaster impacts """

    df_c3 = calculation2(project_object, disasters)

    df_v1 = df[df.type_value == t1]
    dfi3 = {}
    for year in project_object.years():
        k = df_c3[year].values
        df_v1[year] = df_v1.apply(
            lambda x: x[year] * (1 + k[0] if x['with_project'] else 1 + k[1]),
            axis=1)
        dfi3[year] = dfi[year] + k[2] + k[3]

    df = df_v1.append(df[df.type_value != t1])
    df = to_prepare_result(project_object, df, test_mode)
    return df, dfi3


def add_flow(project_object, list_npv, test_mode, name, df, dfi):
    rez = {'type_value': name}
    df_discounted, npv = calculation_npv(project_object, df.copy(), dfi)
    if test_mode:
        rez['value'] = npv
        rez['df'] = df
        rez['df_discounted'] = df_discounted
    else:
        rez['value'] = (npv / 1000000).quantize(Decimal('1.0'))
    list_npv.append(rez)


@time_controller
def calculation_expected_flows(project_object: ProjectObject, test_mode=True):
    list_npv = []

    df_ef1, dfi = flows1(project_object, test_mode)
    add_flow(
        project_object, list_npv, test_mode,
        'Baseline (including project pessimism but without climate impacts)',
        df_ef1, dfi)

    df_ef2 = flows2(project_object, df_ef1, test_mode)
    add_flow(
        project_object, list_npv, test_mode,
        'Impacts from changes in average climate',
        df_ef2, dfi)

    tasks = []
    for disaster in project_object.get_disasters():
        tasks.append(
            ([disaster, ],
             f'Impacts from changes in average climate + disaster impacts ({disaster})'))
    tasks.append((project_object.get_disasters(),
                  'Impacts from all climate and disaster risks'))

    for disaster, name_calculation in tasks:
        df_ef3, dfi_3 = flows3(project_object, disaster, df_ef2.copy(), dfi,
                               test_mode)
        add_flow(
            project_object, list_npv, test_mode,
            name_calculation, df_ef3, dfi_3)

    return list_npv


@time_controller
def calculation_expected_flows_npv_only(project_object: ProjectObject):
    df, dfi = flows1(project_object, False)
    df = flows2(project_object, df, False)
    df, dfi = flows3(project_object, project_object.get_disasters(),
                     df, dfi, False)
    _, npv = calculation_npv(project_object, df, dfi)
    return (npv / 1000000).quantize(Decimal('1.0'))


@time_controller
def calculations_for_graph(project_object: ProjectObject):
    project_object.load_dataset()
    project_object.reset_sa_from_project()
    _data = []
    for level_of_climate_impact in range(0, 101, 10):
        for baseline_pessimism in range(0, 101, 10):
            project_object.set_sa(level_of_climate_impact / 100,
                                  baseline_pessimism / 100)
            _data.append(
                {'baseline_pessimism': baseline_pessimism,
                 'level_of_climate_impact': level_of_climate_impact,
                 'value': calculation_expected_flows_npv_only(project_object)}
            )
    return _data


@time_controller
def calculations_for_sensitivity_analysis(project_object: ProjectObject):
    project_object.load_dataset()
    _data = []
    for section_data in SA_CROSS_TABLE:
        section = section_data['section']
        for type_value_data in section_data['parameters']:
            if section == 'climate_conditions':
                name = type_value_data['name']
                type_value = type_value_data['type_value']
                for level in range(0, 101, 25):
                    project_object.set_climate_parametrs_by_name(
                        section, type_value, level / 100)
                    npv = calculation_expected_flows_npv_only(project_object)
                    _data.append(
                        {'section': 'sa',
                         'level': level,
                         'type_value': name,
                         'value': npv}
                    )
            elif section == 'disaster':
                for disaster in project_object.get_disasters():
                    _name = type_value_data['name']
                    name = f'{_name} ({disaster})'
                    type_value = type_value_data['type_value']
                    for level in range(0, 101, 25):
                        project_object.set_climate_parametrs_by_name(
                            section, type_value, level / 100, disaster=disaster)
                        npv = calculation_expected_flows_npv_only(
                            project_object)
                        _data.append(
                            {'section': 'sa',
                             'level': level,
                             'type_value': name,
                             'value': npv}
                        )
            else:
                name = type_value_data
                for level in range(0, 101, 25):
                    project_object.reset_sa_from_project()
                    if name == 'All climate impacts':
                        project_object.set_sa(
                            level / 100, project_object.baseline_pessimism)
                    elif name == 'Baseline scenario':
                        project_object.sa.baseline_pessimism = level / 100

                    npv = calculation_expected_flows_npv_only(
                        project_object)
                    _data.append(
                        {'section': section,
                         'level': level,
                         'type_value': name,
                         'value': npv}
                    )
    return _data


@time_controller
def calculations_for_sa_discount_rate(project_object: ProjectObject):
    project_object.load_dataset()
    _data = []
    name = 'discount_rate'
    for level in [1, 2, 3, 6, 8, 12]:
        project_object.reset_sa_from_project()
        project_object.sa.discount_rate = level / 100
        npv = calculation_expected_flows_npv_only(project_object)
        _data.append(
            {'section': name,
             'level': level,
             'type_value': name,
             'value': npv}
        )
    return _data


