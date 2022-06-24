from .calculations.expected_flows import calculations_for_graph, \
    calculation_expected_flows, calculations_for_sensitivity_analysis, \
    calculations_for_sa_discount_rate
from .calculations.project_object import ProjectObject
from .cruid import calculations_to_database, set_project_status, \
    analysis_result_to_database


def calculations_task(project_id: int):
    project_object = ProjectObject(project_id)
    if project_object:
        set_project_status(project_id, True)

        _data = calculations_for_graph(project_object)
        calculations_to_database(project_object, _data)

        _data = calculation_expected_flows(project_object, test_mode=False)
        analysis_result_to_database(project_object, _data, 'base')

        _data = calculations_for_sensitivity_analysis(project_object)
        analysis_result_to_database(project_object, _data, 'sa')

        _data = calculations_for_sa_discount_rate(project_object)
        analysis_result_to_database(project_object, _data, 'discount_rate')

        set_project_status(project_id, False, True)
