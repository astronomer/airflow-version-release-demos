from airflow.sdk import dag, task, Asset

@dag(
    schedule="@daily", # if manual runs are not allowed, a schedule needs to be set. PR 61833
    allowed_run_types=["scheduled", "backfill"])
def cannot_run_manually():

    @task(outlets=Asset("TEST"))
    def print_hello():
        print("Hello")

    print_hello()


cannot_run_manually()
