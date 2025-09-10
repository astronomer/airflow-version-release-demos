from airflow.sdk import dag, task

@dag
def plugin_dag():
    @task
    def print_hello():
        print("Hello, World!")

    print_hello()

plugin_dag()