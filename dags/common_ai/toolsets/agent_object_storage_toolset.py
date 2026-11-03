"""
## Agent object storage toolset

`ObjectStorageToolset` gives the agent read-only access to the files under one
path: `list_files`, `get_file_info` and `read_file`. The path can be anything
`ObjectStoragePath` opens (`s3://`, `gs://`, `file://` and others). Paths
outside the root are refused. New in Common AI 1.0.
"""

from airflow.providers.common.ai.toolsets.object_storage import ObjectStorageToolset
from airflow.sdk import dag, task

MANIFESTS = "file:///usr/local/airflow/include/cargo_manifests"


@dag(tags=["common_ai"])
def agent_object_storage_toolset():
    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="Use the file tools to answer. Answer in two sentences at most.",
        toolsets=[ObjectStorageToolset(path=MANIFESTS)],
    )
    def find_riskiest_manifest():
        return "Which cargo manifest has the highest risk, and why?"

    find_riskiest_manifest()


agent_object_storage_toolset()
