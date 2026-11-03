"""
## OpenAI Agents SDK tools

An OpenAI Agents SDK agent with a Common AI toolset as its tools. `AirflowTools`
wraps `ObjectStorageToolset`, so the agent gets the toolset's path checks and
Airflow's secret masking on every tool result. `AirflowTraceProcessor` records
the SDK's traces as the task's OpenTelemetry spans instead of sending them to
OpenAI. The API key comes from the `pydanticai_default` connection.
New in Common AI 1.0.
"""

from airflow.sdk import BaseHook, dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


@dag(tags=["common_ai"])
def openai_agents_tools():
    @task
    def run_openai_agent():
        from agents import Agent, OpenAIChatCompletionsModel, Runner, set_trace_processors
        from openai import AsyncOpenAI

        from airflow.providers.common.ai.tools.openai_agents import AirflowTools, AirflowTraceProcessor
        from airflow.providers.common.ai.tools.tracing import agent_framework_tracing
        from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset

        set_trace_processors([AirflowTraceProcessor()])
        api_key = BaseHook.get_connection("pydanticai_default").password
        agent = Agent(
            name="customs_officer",
            model=OpenAIChatCompletionsModel(model="gpt-5-mini", openai_client=AsyncOpenAI(api_key=api_key)),
            instructions="You are a customs officer. Use the file tools to answer.",
            tools=AirflowTools(ObjectStorageToolset(path=MANIFESTS)),
        )
        with agent_framework_tracing():
            answer = Runner.run_sync(agent, "Which manifests declare hazardous cargo?").final_output
        print(answer)
        return answer

    run_openai_agent()


openai_agents_tools()
