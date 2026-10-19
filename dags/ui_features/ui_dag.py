from airflow.sdk import dag, task_group, task, chain


@dag
def ui_dag():

    @task
    def my_task_1():
        pass

    @task_group()
    def my_task_group():

        @task
        def my_task_2():
            pass

        @task
        def my_task_3():
            pass

        chain(my_task_2(), my_task_3())

    chain(my_task_1(), my_task_group())


ui_dag()
