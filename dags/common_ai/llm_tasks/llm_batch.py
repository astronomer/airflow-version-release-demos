"""
## LLM batch

`@task.llm_batch` sends a list of prompts to the provider's batch API (OpenAI or
Anthropic, picked from the model) instead of one request per prompt. Results
don't go to XCom: they're written as JSONL under `result_path`, and the task
returns a manifest that says where they are and how many requests succeeded.

Batch jobs run asynchronously on the provider's side, so this can take minutes.
`deferrable=True` hands the waiting to the triggerer. New in Common AI 1.0.
"""

from airflow.sdk import ObjectStoragePath, dag, task


@dag(tags=["common_ai"])
def llm_batch():
    @task
    def get_planets():
        return ["Mars", "Europa", "Titan"]

    @task.llm_batch(
        llm_conn_id="pydanticai_default",
        result_path="file:///tmp/llm_batch/{{ dag.dag_id }}/{{ run_id }}",
        system_prompt="Answer in one sentence.",
        deferrable=True,
        poll_interval=30,
    )
    def describe_planets(planets):
        return [f"What is the biggest challenge of landing cargo on {planet}?" for planet in planets]

    @task
    def print_results(manifest):
        print(f"Manifest: {manifest}")
        print(ObjectStoragePath(manifest["result_uri"]).read_text())

    print_results(describe_planets(get_planets()))


llm_batch()
