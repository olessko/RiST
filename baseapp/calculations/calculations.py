from decimal import Decimal
import numpy as np
import pandas as pd

from .project_object import ProjectObject
from .time_contoller import time_controller

return_period_name = 'Return period (years)'


def add_df(df1, df2):
    return pd.concat([df1, pd.DataFrame.from_records(df2)])


@time_controller
def calculations_1_1(project_object: ProjectObject, with_project):
    sa = project_object.sa.climate_conditions
    df = project_object.get_climate_conditions(with_project=with_project)
    df['sa'] = df["type_value"].map(sa)

    date_index = project_object.climate_conditions_years
    for _date in date_index:
        df[_date] = df.apply(
            lambda x: x[_date] * (x['sa'] if x['impact'] else 1 - x['sa']),
            axis=1)
    del df['impact']
    del df['sa']
    return df.groupby(by=['type_value', 'cost'], as_index=False).sum()


@time_controller
def calculations_1_2(project_object: ProjectObject, df):
    date_index = project_object.climate_conditions_years
    for count, _date in enumerate(date_index):
        df.rename(columns={_date: f'date{count}'}, inplace=True)

    for year in project_object.years():
        if year <= date_index[0]:
            k = (year - project_object.start_year) / (
                    date_index[0] - project_object.start_year)
            k_id = 'date0'
        else:
            k = (year - project_object.start_year) / (
                    date_index[1] - project_object.start_year)
            k_id = 'date1'
        df[year] = df.apply(
            lambda x: (Decimal(k) * x[k_id]).quantize(Decimal('1.0000')),
            axis=1)

    for count, _date in enumerate(date_index):
        del df[f'date{count}']
    return df


@time_controller
def calculation2_1(project_object: ProjectObject, disaster):
    sa = project_object.sa.disaster_impacts[disaster]
    sa_year = sa.get('year', None)
    sa_value = sa.get('value', None)
    df = project_object.get_disaster_impacts(disaster)
    df['sa'] = df.apply(
        lambda x:
        sa_year if x['type_value'] == return_period_name else sa_value,
        axis=1)
    years = project_object.disaster_impacts_years
    df[years[0]] = df.apply(
        lambda x: x[years[0]] * (0 if x['impact'] else 1), axis=1)
    for i in range(1, len(years)):
        df[years[i]] = df.apply(
            lambda x: x[years[i]] * (x['sa'] if x['impact'] else 1 - x['sa']),
            axis=1)
    del df['impact']
    del df['sa']
    return df.groupby(by=['level_id', 'level', 'type_value'],
                      as_index=False).sum()


def fun_calculation2_2(x, k, k_id1, k_id0):
    if x['type_value'] == return_period_name:
        rez = k / x[k_id1] - k / x[k_id0] + 1 / x[k_id0]
    else:
        rez = k * (x[k_id1] - x[k_id0]) + x[k_id0]
    return rez.quantize(Decimal('1.0000'))


@time_controller
def calculation2_2(project_object: ProjectObject, df):
    years = project_object.disaster_impacts_years
    for count, year in enumerate(years):
        df.rename(columns={year: f'date{count}'}, inplace=True)

    for year in project_object.years():
        num_years = 1 if year <= years[1] else 2
        k = Decimal((year - years[num_years - 1]) / (
                    years[num_years] - years[num_years - 1]))
        k_id1 = f'date{num_years}'
        k_id0 = f'date{num_years - 1}'
        df[year] = df.apply(fun_calculation2_2, axis=1, args=(k, k_id1, k_id0))

    for count, year in enumerate(years):
        del df[f'date{count}']

    df.sort_index(inplace=True)
    return df


@time_controller
def calculation2_3(project_object: ProjectObject, df):
    df_date = df[df.type_value == return_period_name]
    df = df[df.type_value != return_period_name]

    for year in project_object.years():
        v_date = df_date[year].values
        k = {4: v_date[3]}
        for i in range(3):
            k[i+1] = v_date[i] - v_date[i + 1]
        df[year] = df[year] * df['level_id'].map(k)

    del df['level_id']
    del df['level']
    df = df.groupby(by=['type_value'], as_index=True).sum()
    return df


@time_controller
def calculation2(project_object: ProjectObject, disasters):
    list_df = []
    for disaster in disasters:
        df = calculation2_1(project_object, disaster)
        df = calculation2_2(project_object, df)
        df = calculation2_3(project_object, df)
        df.reset_index(inplace=True)
        list_df.append(df)
    df = list_df[0]
    if len(list_df) > 1:
        for i in range(1, len(list_df)):
            df = add_df(df, list_df[i])
        df = df.groupby(by=['type_value'], as_index=False).sum()

    tv = {'Impact on quantity produced (% of yearly output with project)': 0,
          'Impact on quantity produced (% of yearly output without project)': 1,
          'Reconstruction costs (CAPEX) (USD)': 2,
          'Additional out-of-system impacts (USD)': 3
          }
    df['id'] = df['type_value'].map(tv)
    df = df.set_index('id')
    return df.sort_index(sort_remaining=True)


@time_controller
def calculation_npv(project_object: ProjectObject, df, invesment_dict,
                    test_mode=True):
    del df['cost']
    df = df.groupby(by=['type_value', 'with_project'], as_index=False).sum()

    time_saving = 'Time Savings (USD)'
    for year in project_object.years():
        df[year] = df.apply(
            lambda x: x[year] if x['with_project'] else -x[year],
            axis=1)
        df['discounted'] = df.apply(
            lambda x: 'costs' if x['type_value'] != time_saving else 'benefits',
            axis=1)

    del df['type_value']
    del df['with_project']
    invesment_dict['discounted'] = 'costs'
    # df = pd.concat([df, invesment_dict])
    df = df.append(invesment_dict, ignore_index=True)
    df = df.groupby(by=['discounted'], as_index=False).sum()

    for year in project_object.years():
        k = pow(Decimal(1 + project_object.discount_rate),
                Decimal(year + 1 - project_object.start_year))
        df[year] = df.apply(lambda x: (x[year] / k).quantize(Decimal('1.00')),
                            axis=1)
    d1 = df[df.discounted == 'benefits'].drop('discounted', axis='columns')
    d2 = df[df.discounted == 'costs'].drop('discounted', axis='columns')
    npv = np.sum(d1.values, axis=1)[0] - np.sum(d2.values, axis=1)[0]

    if test_mode:
        return df, npv
    else:
        return npv
