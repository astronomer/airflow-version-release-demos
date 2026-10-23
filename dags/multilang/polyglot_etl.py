from airflow.sdk import dag, task


@dag(tags=["multilang"])
def polyglot_etl():
    @task.stub(queue="golang")
    def extract(): ...

    @task.stub(queue="java")
    def transform(data): ...

    @task.stub(queue="typescript")
    def load(total): ...

    load(transform(extract()))


polyglot_etl()
