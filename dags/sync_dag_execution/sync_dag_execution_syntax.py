from airflow.sdk import dag, task

@dag
def sync_dag_execution():
    @task
    def print_hello():
        import time 
        time.sleep(20)
        return "hello_world"

    print_hello()

sync_dag_execution()