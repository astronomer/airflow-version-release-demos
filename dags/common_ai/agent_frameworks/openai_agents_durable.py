"""
## OpenAI Agents SDK durable

`run_durably_sync` runs an OpenAI Agents SDK agent so that a task retry replays
the model and tool calls the failed try already completed, instead of running
them again. On Airflow 3.3 and later the journal is kept in the task state
store; it's deleted once a run succeeds.

To show the replay, the agent's last step is `publish_answer`, which simulates a
worker crash on try 1 by exiting the task process. On try 2 the model calls and
the `read_file` calls replay from the journal (no tool-call groups in the log),
and only `publish_answer` runs live. New in Common AI 1.0.
"""

import os
from datetime import timedelta

from airflow.sdk import BaseHook, dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


def publish_answer(answer: str) -> str:
    """Publish the final answer. Call this once, with the complete answer."""
    try_number = int(os.environ.get("AIRFLOW_CTX_TRY_NUMBER", "1"))
    if try_number == 1:
        print("Simulating a worker crash on try 1")
        os._exit(1)
    print(f"Published on try {try_number}: {answer}")
    return "published"


@dag(tags=["common_ai"])
def openai_agents_durable():
    @task(retries=1, retry_delay=timedelta(seconds=5))
    def run_durable_agent():
        from agents import Agent, OpenAIChatCompletionsModel, RunConfig, function_tool
        from openai import AsyncOpenAI

        from airflow.providers.common.ai.durable.openai_agents import run_durably_sync
        from airflow.providers.common.ai.tools.openai_agents import AirflowTools
        from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset

        api_key = BaseHook.get_connection("pydanticai_default").password
        agent = Agent(
            name="customs_officer",
            model=OpenAIChatCompletionsModel(model="gpt-5-mini", openai_client=AsyncOpenAI(api_key=api_key)),
            instructions=(
                "You are a customs officer. Use the file tools to answer, then call publish_answer "
                "with your answer, then reply with the answer."
            ),
            tools=[*AirflowTools(ObjectStorageToolset(path=MANIFESTS)), function_tool(publish_answer)],
        )
        result = run_durably_sync(
            agent,
            "Which manifests have an expired pilot certification?",
            run_config=RunConfig(tracing_disabled=True),
        )
        return result.final_output

    run_durable_agent()


openai_agents_durable()
