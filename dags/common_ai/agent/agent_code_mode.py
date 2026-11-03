"""
## Agent code mode

`CodeMode` from `pydantic-ai-harness`, passed as a capability. Instead of
calling tools one at a time, the model writes a short Python program that calls
them, and the program runs in a sandboxed interpreter. That saves model round
trips when an answer needs many tool calls, here one `read_file` per manifest.
New in Common AI 1.0 (it replaces the `code_mode` parameter).
"""

from pydantic_ai_harness import CodeMode

from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset
from airflow.sdk import dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


@dag(tags=["common_ai"])
def agent_code_mode():
    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="You are a customs officer. Write Python that calls the tools to answer.",
        toolsets=[ObjectStorageToolset(path=MANIFESTS)],
        capabilities=[CodeMode(max_tool_calls=50)],
    )
    def total_declared_tonnes():
        return "Read every cargo manifest. What is the total declared tonnage per manifest, and overall?"

    total_declared_tonnes()


agent_code_mode()
