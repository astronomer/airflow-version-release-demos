from airflow.sdk import dag, task, chain
import random

@dag(tags=["Java SDK"])
def java_task_syntax_example():

    @task
    def extract():
        numbers = [random.randint(1, 100) for _ in range(random.randint(3, 6))]
        return {"numbers": numbers}

    @task.stub(queue="java")
    def transform(): ...

    @task
    def load(result):
        return result

    extracted = extract()
    transformed = transform()

    chain(extracted, transformed)
    load(transformed)


java_task_syntax_example()
