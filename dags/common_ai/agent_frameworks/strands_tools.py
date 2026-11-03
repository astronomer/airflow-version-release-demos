"""
## Strands tools

A Strands Agents agent with a Common AI toolset as its tools. The `AirflowTools`
plugin wraps `ObjectStorageToolset`, so the agent gets the toolset's path checks
and Airflow's secret masking on every tool result. The model is OpenAI's
`gpt-5-mini` through Strands' `OpenAIModel`, with the API key from the
`pydanticai_default` connection. New in Common AI 1.0.
"""

from airflow.sdk import BaseHook, dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


@dag(tags=["common_ai"])
def strands_tools():
    @task
    def run_strands_agent():
        from strands import Agent
        from strands.models.openai import OpenAIModel

        from airflow.providers.common.ai.tools.strands import AirflowTools
        from airflow.providers.common.ai.tools.tracing import agent_framework_tracing
        from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset

        api_key = BaseHook.get_connection("pydanticai_default").password
        with agent_framework_tracing():
            agent = Agent(
                model=OpenAIModel(client_args={"api_key": api_key}, model_id="gpt-5-mini"),
                plugins=[AirflowTools(ObjectStorageToolset(path=MANIFESTS))],
                system_prompt="You are a customs officer. Use the file tools to answer.",
                callback_handler=None,
            )
            answer = str(agent("Which manifest is low risk, and what does it carry?"))
        print(answer)
        return answer

    run_strands_agent()


strands_tools()
