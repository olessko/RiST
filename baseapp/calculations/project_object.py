from decimal import Decimal

import pandas as pd

from ..cruid import get_project_object, scenario_from_database, \
    disasters_from_database, climate_conditions_from_database, \
    change_disaster_impact_from_database, sensitivity_analysis_from_database


class SensitivityAnalysisParametrs:
    def __init__(self, _id):
        _object = get_project_object(_id)
        if _object:
            self.discount_rate = _object.discount_rate / 100
            self.threshold_below_for_risk = _object.threshold_below_for_risk
            self.level_of_climate_impact = _object.level_of_climate_impact / 100
            self.baseline_pessimism = _object.baseline_pessimism / 100

            self.climate_conditions = sensitivity_analysis_from_database(
                _object, 'climate_conditions')
            self.disaster_impacts = {}
            for disaster in disasters_from_database(_id):
                self.disaster_impacts[
                    disaster] = sensitivity_analysis_from_database(
                    _object, 'disaster', disaster)

    def set_climate_parametrs(self, value):
        decimal_value = Decimal(value)
        for disaster in self.disaster_impacts.keys():
            disaster_impact = self.disaster_impacts[disaster]
            disaster_impact['year'] = decimal_value
            disaster_impact['value'] = decimal_value
        for x in self.climate_conditions.keys():
            self.climate_conditions[x] = decimal_value

    def set_climate_parametrs_by_name(self, section, name, value,
                                      disaster=None):
        decimal_value = Decimal(value)
        if section == 'climate_conditions':
            self.climate_conditions[x] = decimal_value
        elif section == 'disaster':
            disaster_impact = self.disaster_impacts[disaster]
            disaster_impact['name'] = decimal_value
        else:
            if name == 'All climate impacts':
                self.set_climate_parametrs(decimal_value)
            elif name == 'Baseline scenario':
                self.baseline_pessimism = decimal_value
            elif name == 'Discount rate':
                self.discount_rate = decimal_value


class ProjectObject:
    def __init__(self, _id):
        self.id = _id
        _object = self.get_project_object()
        if _object:
            self.name = _object.name
            self.start_year = _object.start_year
            self.lifetime = _object.lifetime
            self.discount_rate = _object.discount_rate / 100
            self.threshold_below_for_risk = _object.threshold_below_for_risk
            self.level_of_climate_impact = _object.level_of_climate_impact / 100
            self.baseline_pessimism = _object.baseline_pessimism / 100

        self.sa = SensitivityAnalysisParametrs(self.id)
        self.optimistic_scenario = None
        self.pesimistic_scenario = None
        self.climate_conditions = None
        self.climate_conditions_years = None
        self.disasters = None
        self.disaster_impacts = None
        self.disaster_impacts_years = None

    def get_project_object(self):
        return get_project_object(self.id)

    def get_optimistic_scenario(self):
        if self.optimistic_scenario is None:
            _object = self.get_project_object()
            self.optimistic_scenario = scenario_from_database(
                _object.optimistic_scenario, _object)
        return self.optimistic_scenario

    def get_pesimistic_scenario(self):
        if self.pesimistic_scenario is None:
            _object = self.get_project_object()
            self.pesimistic_scenario = scenario_from_database(
                _object.pesimistic_scenario, _object)
        return self.pesimistic_scenario

    def get_disasters(self):
        if self.disasters is None:
            self.disasters = disasters_from_database(self.id)
        return self.disasters

    def get_climate_conditions(self, with_project=None):
        if self.climate_conditions is None:
            self.climate_conditions, c_years = climate_conditions_from_database(
                self, True)
            df2, _ = climate_conditions_from_database(self, False)
            self.climate_conditions = pd.concat(
                [self.climate_conditions, pd.DataFrame.from_records(df2)])
            self.climate_conditions_years = c_years
        df = self.climate_conditions.copy()
        if with_project is not None:
            df = df[df.with_project == with_project].drop(['with_project'],
                                                          axis='columns')
        return df

    def get_disaster_impacts(self, disaster_name=None):
        if self.disaster_impacts is None:
            self.disaster_impacts = {}
            for disaster in self.get_disasters():
                df, di_years = change_disaster_impact_from_database(self,
                                                                    disaster)
                self.disaster_impacts[disaster] = df
                self.disaster_impacts_years = di_years
        if disaster_name is not None:
            return self.disaster_impacts[disaster_name].copy()
        else:
            return self.disaster_impacts

    def years(self):
        for year in range(self.start_year, self.start_year + self.lifetime):
            yield year

    def set_sa(self, level_of_climate_impact, baseline_pessimism):
        self.sa.level_of_climate_impact = level_of_climate_impact
        self.sa.baseline_pessimism = baseline_pessimism
        self.sa.set_climate_parametrs(self.level_of_climate_impact)

    def reset_sa_from_project(self):
        self.sa.discount_rate = self.discount_rate
        self.sa.threshold_below_for_risk = self.threshold_below_for_risk
        self.sa.level_of_climate_impact = self.level_of_climate_impact
        self.sa.baseline_pessimism = self.baseline_pessimism
        self.sa.set_climate_parametrs(self.level_of_climate_impact)

    def set_climate_parametrs_by_name(self, section, name, value,
                                      disaster=None):
        self.reset_sa_from_project()
        self.sa.set_climate_parametrs_by_name(section, name, value, disaster)

    def load_dataset(self):
        self.get_optimistic_scenario()
        self.get_pesimistic_scenario()
        self.get_disasters()
        self.get_climate_conditions()
        self.get_disaster_impacts()
