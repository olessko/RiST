import uuid, base64
from io import BytesIO
from matplotlib import pyplot

from .cruid import analysis_result_from_database_to_df, \
    analysis_result_from_database_to_df_for_plot, calculations_from_database


def generate_code():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]


def get_graph():
    buffer = BytesIO()
    pyplot.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_chart_discount_rate(project_object):
    df = analysis_result_from_database_to_df_for_plot(project_object,
                                                      'discount_rate')
    pyplot.switch_backend('AGG')
    fig = pyplot.figure(figsize=(10, 4))
    pyplot.plot(df['level'], df['value'], color='gray', marker='o',
                linestyle='dashed')
    pyplot.grid(True)
    # pyplot.title('Sensitivity analysis - role of the discount rate')
    pyplot.xlabel('discount rate, %')
    pyplot.ylabel('NPV(USD, millions)')
    pyplot.tight_layout()
    chart = get_graph()
    return chart


def get_chart_sa(project_object):
    df = analysis_result_from_database_to_df(project_object, 'sa')
    pyplot.switch_backend('AGG')
    pyplot.style.use('_mpl-gallery')
    fig = pyplot.figure(figsize=(10, 4))
    position = df['type_value']
    value = df['k']
    pyplot.barh(position, value)
    pyplot.xlabel('NPV(USD, millions)')
    pyplot.gca().invert_yaxis()

    pyplot.tight_layout()
    chart = get_graph()
    return chart


def get_chart_graph(project_object):
    df = calculations_from_database(project_object)
    pyplot.switch_backend('AGG')
    pyplot.style.use('_mpl-gallery')
    fig = pyplot.figure(figsize=(5, 5))
    levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    pyplot.contourf(levels, levels, df)
    pyplot.xlabel('Baseline scenario 0% = optimistic, 100% = pessimistic')
    # pyplot.gca().invert_yaxis()
    pyplot.ylabel('0% = no/low impact, 100% high impact')

    pyplot.tight_layout()
    chart = get_graph()
    return chart
