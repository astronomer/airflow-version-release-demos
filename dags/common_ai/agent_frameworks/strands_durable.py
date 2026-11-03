"""
## Strands durable

`invoke_durably` runs a Strands agent so that a task retry resumes from the last
agent cycle it finished, instead of starting over. On Airflow 3.3 and later the
agent's state is kept in the task state store.

To show the resume, the agent's last step is `publish_answer`, which simulates a
worker crash on try 1 by exiting the task process. On try 2 the agent picks up
from its last checkpoint, so the `read_file` calls from try 1 don't run again.
New in Common AI 1.0.
"""

import os
from datetime import timedelta
from functools import partial

from airflow.sdk import BaseHook, dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


@dag(tags=["common_ai"])
def strands_durable():
    @task(retries=1, retry_delay=timedelta(seconds=5))
    def run_durable_strands_agent():
        from strands import Agent, tool
        from strands.models.openai import OpenAIModel

        from airflow.providers.common.ai.durable.strands import invoke_durably
        from airflow.providers.common.ai.tools.strands import AirflowTools
        from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset

        @tool
        def publish_answer(answer: str) -> str:
            """Publish the final answer. Call this once, with the complete answer."""
            try_number = int(os.environ.get("AIRFLOW_CTX_TRY_NUMBER", "1"))
            if try_number == 1:
                print("Simulating a worker crash on try 1")
                os._exit(1)
            print(f"Published on try {try_number}: {answer}")
            return "published"

        api_key = BaseHook.get_connection("pydanticai_default").password
        agent = partial(
            Agent,
            model=OpenAIModel(client_args={"api_key": api_key}, model_id="gpt-5-mini"),
            plugins=[AirflowTools(ObjectStorageToolset(path=MANIFESTS))],
            tools=[publish_answer],
            system_prompt=(
                "You are a customs officer. Use the file tools to answer, then call publish_answer "
                "with your answer, then reply with the answer."
            ),
            callback_handler=None,
        )
        return str(invoke_durably(agent, "What is the total declared tonnage across all manifests?"))

    run_durable_strands_agent()


strands_durable()
