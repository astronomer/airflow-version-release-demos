from airflow.sdk import dag, task, result

@dag(tags=["wait result"])
def results_dag():

    @result
    @task
    def my_task():
        return "hello!"

    my_task()


    @task(task_id=f"task_i")
    def my_task_2():
        return "bye!"

    my_task_2()


results_dag()
