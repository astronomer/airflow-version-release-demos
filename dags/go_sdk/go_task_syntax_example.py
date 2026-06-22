import random

from airflow.sdk import dag, task, chain


@dag(tags=["go sdk"])
def go_task_syntax_example():
    @task
    def extract():
        numbers = [random.randint(1, 100) for _ in range(random.randint(3, 6))]
        return {"numbers": numbers}

    @task.stub(queue="golang")
    def transform(): ...

    @task
    def load(result):
        return result

    extracted = extract()
    transformed = transform()
    chain(extracted, transformed)
    load(transformed)


go_task_syntax_example()
