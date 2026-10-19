from airflow.sdk import dag, task, task_group


def overdrawn_or_done(*, loop):
    return loop.result["balance"] < 0 or loop.result["transactions"] == []


@dag(tags=["task_loop"])
def basic_task_loop_drain_list():

    @task
    def my_upstream_task():
        import random

        return {
            "balance": 100,
            "transactions": [
                random.randint(-50, 30) for _ in range(random.randint(5, 10))
            ],
        }

    @task_group
    def my_task_group(my_account):
        @task
        def my_task_1(my_account, *, loop):
            return my_account if loop.index == 0 else loop.previous

        @task
        def my_task_2(my_account):
            transaction = my_account["transactions"][0]
            balance = my_account["balance"] + transaction
            print(f"Applied {transaction}, balance is now {balance}")
            return {"balance": balance, "transactions": my_account["transactions"][1:]}

        my_task_2(my_task_1(my_account))

    @task
    def my_downstream_task(my_results):
        print(f"Final balance: {my_results[-1]['balance']}")

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_account=_my_upstream_task).loop(
        max_iterations=10, until=overdrawn_or_done
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_task_2"].output)


basic_task_loop_drain_list()
