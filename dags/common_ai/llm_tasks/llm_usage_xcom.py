"""
## LLM usage XCom

The LLM operators push the run's token usage and cost to XCom under the key
`usage`: requests, input, output and total tokens, tool calls, cache tokens,
and the cost in USD as a string (`None` when the model has no price). New in
Common AI 1.1.
"""

from airflow.sdk import dag, task


@dag(tags=["common_ai"])
def llm_usage_xcom():
    @task.llm(llm_conn_id="pydanticai_default", system_prompt="Answer in one sentence.")
    def describe_ceres():
        return "What is Ceres?"

    @task
    def print_usage(ti=None):
        usage = ti.xcom_pull(task_ids="describe_ceres", key="usage")
        print(f"Usage: {usage}")
        print(f"Total tokens: {usage['total_tokens']}, cost: {usage['cost']} USD")

    describe_ceres() >> print_usage()


llm_usage_xcom()
