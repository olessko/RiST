from ..cruid import climate_conditions_from_database, \
    sensitivity_analysis_from_database


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
    df_cc = df.groupby(by=['type value', 'cost']).mean()

    df = df_cc.copy()
    for count, _date in enumerate(date_index):
        df.rename(columns={_date: f'date{count}'}, inplace=True)

    start_year = project_object.start_year
    for year in range(start_year, start_year+project_object.lifetime):
        if year <= date_index[0]:
            k = (year - start_year) / (date_index[0] - start_year)
            k_id = 'date0'
        else:
            k = (year - start_year) / (date_index[1] - start_year)
            k_id = 'date1'
        df[year] = df.apply(lambda x: k * x[k_id], axis=1)

    del df['date0']
    del df['date1']

    return df_cc, df
