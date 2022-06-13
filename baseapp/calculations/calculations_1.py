from decimal import Decimal

from ..cruid import climate_conditions_from_database, \
    sensitivity_analysis_from_database, change_disaster_impact_from_database


def calculations_1_1(project_object, with_project):
    sa = sensitivity_analysis_from_database(project_object,
                                            'climate_conditions')
    df = climate_conditions_from_database(project_object, with_project)
    df['sa'] = df["type value"].map(sa)

    date_index = [2030, 2050]
    for _date in date_index:
        df[_date] = df.apply(
            lambda x: x[_date] * (x['sa'] if x['impact'] else 1 - x['sa']),
            axis=1)
    del df['impact']
    del df['sa']
    df_cc = df.groupby(by=['type value', 'cost']).sum()

    df = df_cc.copy()
    for count, _date in enumerate(date_index):
        df.rename(columns={_date: f'date{count}'}, inplace=True)

    start_year = project_object.start_year
    for year in range(start_year, start_year + project_object.lifetime):
        if year <= date_index[0]:
            k = (year - start_year) / (date_index[0] - start_year)
            k_id = 'date0'
        else:
            k = (year - start_year) / (date_index[1] - start_year)
            k_id = 'date1'
        df[year] = df.apply(
            lambda x: (Decimal(k) * x[k_id]).quantize(Decimal('1.0000')),
            axis=1)

    del df['date0']
    del df['date1']

    return df_cc, df


def calculation2(project_object, disaster_impact):
    sa = sensitivity_analysis_from_database(project_object, 'disaster',
                                            disaster=disaster_impact)
    sa_year = sa.get('year', None)
    sa_value = sa.get('value', None)
    df = change_disaster_impact_from_database(project_object, disaster_impact)
    return_period_name = 'Return period (years)'
    df_date = df[df.type_value == return_period_name]
    df_value = df[df.type_value != return_period_name]

    date_index = [(2022, 0, 0),
                  (2030, sa_year, sa_value), (2050, sa_year, sa_value)]
    for _date, _sa_year, _sa_value in date_index:
        df_value[_date] = df_value.apply(
            lambda x: x[_date] * (_sa_value if x['impact'] else 1 - _sa_value),
            axis=1)
        df_date[_date] = df_date.apply(
            lambda x: x[_date] * (_sa_year if x['impact'] else 1 - _sa_year),
            axis=1)
    df = df_value.append(df_date)
    del df['impact']
    df_c1 = df.groupby(by=['level_id', 'level', 'type_value'], as_index=False).sum()

    df = df_c1.copy()
    for count, _date in enumerate(date_index):
        df.rename(columns={_date[0]: f'date{count}'}, inplace=True)
    df_date = df[df.type_value == return_period_name]
    df_value = df[df.type_value != return_period_name]

    start_year = project_object.start_year
    for year in range(start_year, start_year + project_object.lifetime):
        if year <= date_index[1][0]:
            k = (year - start_year) / (date_index[1][0] - start_year)
            k_id1 = 'date1'
            k_id0 = 'date0'
        else:
            k = (year - date_index[1][0]) / (
                        date_index[2][0] - date_index[1][0])
            k_id1 = 'date2'
            k_id0 = 'date1'

        df_date[year] = df_date.apply(
            lambda x: (Decimal(k) * (1 / x[k_id1] - 1 / x[k_id0]) + 1 / x[k_id0]).quantize(Decimal('1.0000')),
            axis=1)

        df_value[year] = df_value.apply(
            lambda x: (Decimal(k) * (x[k_id1] - x[k_id0]) + x[k_id0]).quantize(Decimal('1.0000')),
            axis=1)

    df_c2 = df_value.append(df_date)
    del df_c2['date0']
    del df_c2['date1']
    del df_c2['date2']
    df_c2.sort_index(inplace=True)

    df = df_c2.copy()
    df_date = df[df.type_value == return_period_name]
    df_value = df[df.type_value != return_period_name]
    v_type_value = df_value['type_value'].unique()
    list_df = []
    for x in v_type_value:
        list_df.append(df_value[df_value.type_value == x])

    for year in range(start_year, start_year + project_object.lifetime):
        v_date = df_date[year].values
        for i in range(3):
            v_date[i] = v_date[i] - v_date[i+1]

        for v_df in list_df:
            v_df[year] = v_df[year].mul(v_date)
            v_df[year] = v_df[year].apply(
                lambda x: x.quantize(Decimal('1.0000')))

    for num, v_df in enumerate(list_df):
        temp = list_df[num]
        del temp['level_id']
        del temp['level']
        list_df[num] = temp.groupby(by=['type_value'], as_index=True).sum()

    df_c3 = list_df[0]
    for i in range(1, len(list_df)):
        df_c3 = df_c3.append(list_df[i])

    return df_c1, df_c2, df_c3
