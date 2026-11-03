"""
## Agent tool logging

`enable_tool_logging=True` (the default, set explicitly here) adds a
`ToolLoggingCapability` that writes every tool call to the task log as it
happens, with its duration, in a collapsible group. New in Common AI 1.1,
where it replaces the experimental `LoggingToolset`.
"""

from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset
from airflow.sdk import dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


@dag(tags=["common_ai"])
def agent_tool_logging():
    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="You are a customs officer. Use the file tools. Answer in two sentences.",
        toolsets=[ObjectStorageToolset(path=MANIFESTS)],
        enable_tool_logging=True,
    )
    def check_manifests():
        return "Which cargo manifest has customs flags, and what are they?"

    check_manifests()


agent_tool_logging()
