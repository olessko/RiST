from decimal import Decimal

from .calculations import calculations_1_1, calculation_npv, calculation2
from ..cruid import scenario_from_database, disaster_impacts_from_database

v1 = 'Expected change in quantity produced (%)'
v2 = 'Expected change in price (%)'
v3 = 'Expected change in input and operational costs (%)'
v4 = 'Expected change in labor costs (%)'

t1 = 'Time Savings (USD)'
t2 = 'O&M (USD)'
t3 = 'VOC'

crosstable_vt = {v1: t1, v2: t1, v3: t2, v4: t3}
INDEX_DF = ['cost', 'with_project', 'type_value']


def to_prepare_result(project_object, df, test_mode=True):
    start_year = project_object.start_year
    for year in range(start_year, start_year + project_object.lifetime):
        df[year] = df[year].map(lambda x: x.quantize(Decimal('1.00')))
    if test_mode:
        df = df.set_index(INDEX_DF)
        df = df.sort_index(level=INDEX_DF, sort_remaining=True)
        df = df.reset_index()
    return df


def flows1(project_object, test_mode=True):
    """Baseline (including project pessimism but without climate impacts)"""

    discount_rate = Decimal(project_object.discount_rate)

    optimistic_scenario = scenario_from_database(
        project_object.optimistic_scenario, project_object)
    df_optimistic_scenario = optimistic_scenario['df']
    dfi_optimistic_scenario = optimistic_scenario['dfi']

    pesimistic_scenario = scenario_from_database(
        project_object.pesimistic_scenario, project_object)
    df_pesimistic_scenario = pesimistic_scenario['df']
    dfi_pesimistic_scenario = pesimistic_scenario['dfi']

    dfi = {}
    start_year = project_object.start_year
    for year in range(start_year, start_year + project_object.lifetime):
        dfi[year] = dfi_pesimistic_scenario[year] * discount_rate + \
                    dfi_optimistic_scenario[year] * (1 - discount_rate)
        df_optimistic_scenario[year] = df_optimistic_scenario[year].map(
            lambda x: x * (1 - discount_rate))
        df_pesimistic_scenario[year] = df_pesimistic_scenario[year].map(
            lambda x: x * discount_rate)

    df = df_optimistic_scenario.append(df_pesimistic_scenario)
    df = df.groupby(by=INDEX_DF, as_index=False).sum()
    df = to_prepare_result(project_object, df, test_mode)

    df_discounted, nvp = calculation_npv(project_object, df.copy(), dfi)
    return df, df_discounted, nvp, dfi


def flows2i(project_object, df_ef1, with_project):

    df = calculations_1_1(project_object, with_project, test_mode=False)
    df['with_project'] = with_project

    start_year = project_object.start_year
    for year in range(start_year, start_year + project_object.lifetime):
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

    for year in range(start_year, start_year + project_object.lifetime):
        k2 = df_k2[year].values[0]
        k3 = df_k3[year].values[0]
        df2[year] = df2.apply(
            lambda x: x[year] * (k2 if x['type_value'] == t2 else k3), axis=1)

    return df1.append(df2)


def flows2(project_object, df_ef1, dfi, test_mode=True):
    """Impacts from changes in average climate"""
    df = flows2i(project_object, df_ef1, True)
    df = df.append(flows2i(project_object, df_ef1, False))
    df = to_prepare_result(project_object, df, test_mode)

    df_discounted, nvp = calculation_npv(project_object, df.copy(), dfi)
    return df, df_discounted, nvp


def flows3(project_object, disaster_impacts, df, dfi, test_mode=True):
    """Impacts from changes in average climate + disaster impacts """

    df_c3 = calculation2(project_object, disaster_impacts[0], test_mode=False)
    if len(disaster_impacts) > 1:
        for i in range(1, len(disaster_impacts)):
            df_c3.append(calculation2(project_object, disaster_impacts[i],
                                      test_mode=False))
        df_c3 = df_c3.groupby(by=['type_value'], as_index=False).sum()

    tv = {'Impact on quantity produced (% of yearly output with project)': 0,
          'Impact on quantity produced (% of yearly output without project)': 1,
          'Reconstruction costs (CAPEX) (USD)': 2,
          'Additional out-of-system impacts (USD)': 3
          }
    df_c3['id'] = df_c3.apply(
        lambda x: tv.get(x['type_value'], 0), axis=1)
    df_c3 = df_c3.set_index('id')
    df_c3 = df_c3.sort_index(sort_remaining=True)

    df_v1 = df[df.type_value == t1]
    dfi3 = {}
    start_year = project_object.start_year
    for year in range(start_year, start_year + project_object.lifetime):
        k = df_c3[year].values
        df_v1[year] = df_v1.apply(
            lambda x: x[year] * (1 + k[0] if x['with_project'] else k[1]),
            axis=1)
        dfi3[year] = dfi[year] + k[2] + k[3]

    df = df_v1.append(df[df.type_value != t1])
    df = to_prepare_result(project_object, df, test_mode)

    df_discounted, nvp = calculation_npv(project_object, df.copy(), dfi3)
    return df, df_discounted, nvp


def add_flow(list_nvp, test_mode, name, df, df_discounted, nvp):
    rez = {'name': name}
    if test_mode:
        rez['nvp'] = nvp
        rez['df'] = df
        rez['df_discounted'] = df_discounted
    else:
        rez['nvp'] = (nvp/1000000).quantize(Decimal('1.0'))
    list_nvp.append(rez)


def calculation_expected_flows(project_object, test_mode=True):
    list_nvp = []

    df_ef1, df_discounted, nvp, dfi = flows1(project_object, test_mode)
    add_flow(
        list_nvp, test_mode,
        'Baseline (including project pessimism but without climate impacts)',
        df_ef1, df_discounted, nvp)

    df_ef2, df_discounted, nvp = flows2(project_object, df_ef1, dfi, test_mode)
    add_flow(
        list_nvp, test_mode,
        'Impacts from changes in average climate',
        df_ef2, df_discounted, nvp)

    tasks = []
    disaster_impact_all = []
    for disaster_impact in disaster_impacts_from_database(project_object.id):
        disaster_impact_all.append(disaster_impact)
        tasks.append(([disaster_impact, ],
                     f'Impacts from changes in average climate + disaster impacts ({disaster_impact})'))
    tasks.append((disaster_impact_all,
                 'Impacts from all climate and disaster risks'))

    for disaster_impact, name_calculation in tasks:
        df_ef3, df_discounted, nvp = flows3(project_object, disaster_impact,
                                            df_ef2.copy(), dfi, test_mode)
        add_flow(
            list_nvp, test_mode, name_calculation, df_ef3, df_discounted, nvp)

    return list_nvp
