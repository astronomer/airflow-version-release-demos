"""
### Placeholder DAG (not for the registry)

Placeholder downstream DAG for the demo.
"""

from airflow import DAG, Dataset
from airflow.decorators import task
from pendulum import datetime

MY_FOLDER = "even_more_pictures_of_Avery"
my_dataset = Dataset(f"my_blob_storage://{MY_FOLDER}")

with DAG(
    dag_id="second_downstream_toy",
    start_date=datetime(2022, 12, 1),
    schedule=[my_dataset],
    catchup=False,
    tags=["datasets", "taskflow", "toy"]
):

    @task
    def say_hi():
        return "hi"

    say_hi()