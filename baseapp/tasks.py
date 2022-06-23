from .calculations.expected_flows import calculations_for_graph
from .calculations.project_object import ProjectObject
from .cruid import calculations_to_database, set_project_status


def calculations_task(project_id: int):
    project_object = ProjectObject(project_id)
    if project_object:
        set_project_status(project_id, True)

        _data = calculations_for_graph(project_object)
        calculations_to_database(project_object, _data)

        set_project_status(project_id, False, True)
