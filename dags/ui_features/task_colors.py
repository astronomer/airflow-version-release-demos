from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import TaskGroup, chain, dag, task, task_group


class MyYellowOperator(EmptyOperator):
    ui_color = "#f6f187"
    ui_fgcolor = "#000000"


@dag(tags=["ui_features"])
def task_colors():

    @task_group(ui_color="#ef847f", ui_fgcolor="#000000")
    def my_decorated_task_group():
        EmptyOperator(task_id="task_in_decorated_group")

    with TaskGroup(group_id="my_task_group", ui_color="#f8be7f", ui_fgcolor="#000000") as my_task_group:
        EmptyOperator(task_id="task_in_task_group")

    my_subclassed_operator = MyYellowOperator(task_id="my_subclassed_operator")

    my_operator = EmptyOperator(task_id="my_operator")
    my_operator.ui_color = "#b5d88a"
    my_operator.ui_fgcolor = "#000000"

    @task
    def my_task():
        pass

    _my_task = my_task()
    _my_task.operator.ui_color = "#8ba3cd"
    _my_task.operator.ui_fgcolor = "#000000"

    @task
    def my_other_task():
        pass

    _my_other_task = my_other_task()
    _my_other_task.operator.ui_color = "#af86b9"
    _my_other_task.operator.ui_fgcolor = "#000000"

    chain(
        my_decorated_task_group(),
        my_task_group,
        my_subclassed_operator,
        my_operator,
        _my_task,
        _my_other_task,
    )


task_colors()
