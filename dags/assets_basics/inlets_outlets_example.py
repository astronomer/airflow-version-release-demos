from airflow.sdk import Asset, dag, task

my_out_in_asset = Asset("my_out_in_asset")


@dag
def my_out_in_upstream_dag():

    @task
    def get_num():
        import random

        return random.randint(1, 100)

    @task(outlets=[my_out_in_asset])
    def my_outlet_task(num: int, **context):
        outlet_events = context["outlet_events"]
        outlet_events[my_out_in_asset].extra = {"my_random_number": num}
        return 1

    my_outlet_task(num=get_num())


my_out_in_upstream_dag()


@dag  # can be scheduled on an asset but does not have to be to use an asset as an inlet
def my_out_in_downstream_dag():

    @task(inlets=[my_out_in_asset])
    def my_task_with_an_inlet(**context):
        inlet_events = context["inlet_events"]
        print(
            f"Print num from latest inlet event: {inlet_events[my_out_in_asset][-1].extra['my_random_number']}"
        )

    my_task_with_an_inlet()


my_out_in_downstream_dag()
