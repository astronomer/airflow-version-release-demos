from airflow.sdk import dag, task


@dag(tags=["multilang"])
def python_baseline_etl():
    @task
    def extract():
        return {
            "orders": [
                {"id": 1, "amount": 20},
                {"id": 2, "amount": 35},
                {"id": 3, "amount": 45},
            ]
        }

    @task
    def transform(data):
        return sum(order["amount"] for order in data["orders"])

    @task
    def load(total):
        print(f"Total order amount: {total}")

    load(transform(extract()))


python_baseline_etl()
