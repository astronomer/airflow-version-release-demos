from airflow.sdk import dag, task


@dag(tags=["multilang"])
def typescript_stub_etl():
    @task
    def extract():
        return {
            "orders": [
                {"id": 1, "amount": 20},
                {"id": 2, "amount": 35},
                {"id": 3, "amount": 45},
            ]
        }

    @task.stub(queue="typescript")
    def transform(data): ...

    @task
    def load(total):
        print(f"Total order amount: {total}")

    load(transform(extract()))


typescript_stub_etl()
