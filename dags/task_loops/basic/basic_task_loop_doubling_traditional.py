import random

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, chain, task_group


def over_100(*, loop):
    loop_result = loop.result["doubled_number"]
    print(f"Loop result: {loop_result}")
    return loop_result > 100


def get_start_number():
    return random.randint(1, 10)


def get_current_number(my_number, loop):
    return my_number if loop.index == 0 else loop.previous["doubled_number"]


def double_number(my_number):
    return {"doubled_number": my_number * 2}


def print_last_result(my_results):
    print(my_results[-1])


with DAG(
    dag_id="basic_task_loop_doubling_traditional",
    tags=["task_loop", "webinar"],
    render_template_as_native_obj=True,
):
    my_upstream_task = PythonOperator(
        task_id="my_upstream_task",
        python_callable=get_start_number,
    )

    @task_group
    def my_task_group(my_number):
        my_task_1 = PythonOperator(
            task_id="my_task_1",
            python_callable=get_current_number,
            op_kwargs={"my_number": my_number},
        )

        my_task_2 = BashOperator(
            task_id="my_task_2",
            bash_command=(
                "echo 'Iteration {{ loop.index }} of max {{ loop.max_iterations }}, "
                "still looping, the number is: "
                "{{ ti.xcom_pull(task_ids=\"my_task_group.my_task_1\") }}'"
            ),
        )

        my_task_3 = PythonOperator(
            task_id="my_task_3",
            python_callable=double_number,
            op_kwargs={"my_number": "{{ ti.xcom_pull(task_ids='my_task_group.my_task_1') }}"},
        )

        chain(my_task_1, my_task_2, my_task_3)

    _my_task_group = my_task_group.partial(my_number=my_upstream_task.output).loop(
        max_iterations=5, until=over_100
    )

    my_downstream_task = PythonOperator(
        task_id="my_downstream_task",
        python_callable=print_last_result,
        op_kwargs={"my_results": _my_task_group["my_task_3"].output},
    )
