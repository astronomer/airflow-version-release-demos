# Apache Airflow 3.4 Example Dags

This repository contains example Dags and plugins showcasing features and improvements introduced in Apache Airflow 3.4. The project runs on the pre-release Astro Runtime image `runtime-dev:3.4-1-alpha7`.

# How to use this repository

Download the [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) to run Airflow locally in containers. `astro` is the only package you need to install for the Python Dags.

1. Run `git clone https://github.com/astronomer/airflow-version-release-demos.git` on your computer to create a local clone of this repository.
2. Check out the `v3.4` branch: `git checkout v3.4`.
3. Install the Astro CLI by following the steps in the [Astro CLI documentation](https://www.astronomer.io/docs/astro/cli/install-cli).
4. Rename the `.env_example` file to `.env`. If you want to run any of the AI-related Dags, replace the `<your key>` placeholders with your AI API key.
5. Run `astro dev start` in your cloned repository.
6. After your Astro project has started, open the Airflow UI at the URL `astro dev start` prints (`localhost:8080` unless another Astro project is already running).

## What's in this repository

| Folder | What it shows |
|---|---|
| `dags/task_loops/` | Task loops: repeat a task or task group until a condition is met. `basic/` has small loops (doubling, Fibonacci, draining a list, `until` with params or upstream values), `advanced/` has agent and human-in-the-loop loops, and `experiments/` covers edge cases such as loops with mapping, nested task groups and retries. |
| `dags/retry_policies/` | Retry policies: decide per exception whether a task retries, fails or reschedules, including `ExceptionRetryPolicy`, `ChainRetryPolicy` and the AI retry policies from the common AI provider. |
| `dags/common_ai/` | Features that are new in versions 1.0 and 1.1 of the [common AI provider](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/index.html), one Dag per feature. See [Run the AI Dags](#run-the-ai-dags). |
| `dags/multilang/` | The same small ETL pipeline written in Python, Go, Java, TypeScript and YAML, plus `@task.stub` Dags that mix languages. See [Run the multi-language Dags](#run-the-multi-language-dags). |
| `dags/other/` | Asset and time schedules (`AssetAndTimeSchedule`, `AssetOrTimeSchedule`), asset event batching, and dynamically generated Dags. |
| `dags/ui_features/` | Dags used for UI screenshots and UI features, such as task colors, run types, and the `hidden_games` Dag for the scoped plugin examples. |
| `plugins/` | Example plugins, see [Plugins](#plugins). |

## Plugins

All plugins load automatically with `astro dev start`. After changing a plugin, restart the API server with `astro dev restart`.

| Plugin | Feature | Where to look |
|---|---|---|
| `klingon_ui.py` | `ui_translations`: adds Klingon (`tlh`) as a UI language. The Home page and the Dags list are translated. | User menu > Select language > `tlh`. |
| `failed_dags_label.py` | `ui_translations`: overrides one English string inline. | The failed Dags stat on the Home page. |
| `hidden_games_plugin.py` | React apps on the Dag and task overview pages and on an asset tab, scoped with `applies_to`. | The Dag tagged `scoped_plugin_example` (`hidden_games`): tic-tac-toe on the Dag overview, Minesweeper and Slitherlink on the task overviews, Battleships on the `the_high_seas` asset. Other Dags don't show the games. |
| `page_context_plugin.py` | The props Airflow passes to React apps (`dagId`, `taskInstance`, `dagRun`, `dag` and more). | The **Page context** tab of any task instance. |

## Run the AI Dags

The AI Dags use the `pydanticai_default` connection from `.env`. Add your OpenAI API key to it. Most Dags use the model set in the connection (`openai:gpt-4o` in `.env_example`); the OpenAI Agents SDK and Strands Dags in `agent_frameworks/` set `gpt-5-mini` in their code and only take the API key from the connection.

`dags/common_ai/` has one Dag per feature that's new in common AI provider 1.0 or 1.1:

| Dag | Feature | New in |
|---|---|---|
| `llm_tasks/llm_batch` | `@task.llm_batch`: prompts sent to the provider's batch API, results written as JSONL to object storage | 1.0 |
| `llm_tasks/llm_usage_xcom` | Token usage and cost pushed to XCom under the key `usage` | 1.1 |
| `agent/agent_tool_approval` | A tool marked `requires_approval` pauses the task until someone approves the call on the Required Actions page | 1.0 |
| `agent/agent_capabilities` | `capabilities=` with pydantic-ai's `Thinking` | 1.0 |
| `agent/agent_code_mode` | The `CodeMode` capability: the model writes Python that calls the tools | 1.0 |
| `agent/agent_emit_message_history` | `emit_message_history=True` records the agent's transcript in XCom | 1.1 |
| `agent/agent_tool_logging` | `ToolLoggingCapability` logs every tool call | 1.1 |
| `toolsets/agent_object_storage_toolset` | `ObjectStorageToolset`: read-only file access for an agent | 1.0 |
| `agent_frameworks/openai_agents_tools` | Common AI toolsets in an OpenAI Agents SDK agent, with traces recorded as the task's spans | 1.0 |
| `agent_frameworks/openai_agents_durable` | `run_durably_sync`: a task retry replays the calls the failed try completed | 1.0 |
| `agent_frameworks/strands_tools` | Common AI toolsets in a Strands agent | 1.0 |
| `agent_frameworks/strands_durable` | `invoke_durably`: a task retry resumes the Strands agent from its last checkpoint | 1.0 |

The two durable Dags simulate a worker crash on the first try, so you can compare the logs of try 1 and try 2.

The toolset and framework Dags read the cargo manifests in `include/cargo_manifests`. Other AI Dags in this repository: `ai_retry_policies.py` and `chain_retry_policy.py` in `dags/retry_policies/`, and `agent_support_reply.py` and `agent_text_to_sql.py` in `dags/task_loops/advanced/`.

For examples of every common AI provider feature, see [common-ai-provider-example-dags](https://github.com/astronomer/common-ai-provider-example-dags).

The common AI provider adds an **AI Model** tab to the task instances of LLM and agent tasks, showing the model, token usage and cost.

## Run the multi-language Dags

`dags/multilang/` contains one ETL pipeline in several languages:

- `python_baseline_etl.py` is plain Python and runs without extra steps.
- `yaml/yaml_etl.yaml` and `yaml/yaml_etl_python.yaml` are YAML Dags. They need the `AIRFLOW__DAG_PROCESSOR__DAG_IMPORTER_CONFIGS` line from `.env_example`.
- `go/main.go`, `java/JavaEtl.java` and `typescript/typescript_etl.ts` are native Go, Java and TypeScript Dags.
- `<language>_stub_etl.py` are Python Dags whose transform step runs in Go, Java or TypeScript with `@task.stub`. `polyglot_etl.py` runs extract in Go, transform in Java and load in TypeScript.
- `yaml/yaml_etl_typescript.yaml` is a YAML Dag with a TypeScript task.

The native Dags and the stub tasks need compiled artifacts, which are not committed. Their handlers are in the same artifact as each language's native Dag, so one build per language covers both. The coordinator settings (`AIRFLOW__SDK__COORDINATORS` and `AIRFLOW__SDK__QUEUE_TO_COORDINATOR`) are in `.env_example`, and the Dockerfile and `packages.txt` already add Node and a Java runtime to the image.

The build scripts run in Docker, so you don't need Go, a JDK or Node installed locally. Run them from the root of the repository:

```bash
include/go_sdk/build.sh
include/typescript_sdk/build.sh
include/java_sdk/build.sh
```

| Script | SDK | Artifact |
|---|---|---|
| `include/go_sdk/build.sh` | Go SDK `v1.0.0-beta4`, from the Go module proxy | `dags/multilang/go/go_etl` |
| `include/typescript_sdk/build.sh` | TypeScript SDK `@apache-airflow/ts-sdk` `1.0.0-beta2`, from npm | `typescript_etl.min.mjs` in `dags/multilang/typescript/` and `yaml_etl_typescript.min.mjs` in `dags/multilang/yaml/` |
| `include/java_sdk/build.sh` | Java SDK built from a local clone of [apache/airflow](https://github.com/apache/airflow) | `dags/multilang/java/java_etl.jar` |

The Java SDK release that supports Airflow 3.4 is not published yet, so the Java script builds the SDK from source. Clone the repository first:

```bash
git clone https://github.com/apache/airflow.git ~/code/apache/airflow
```

If your clone is somewhere else, set `AIRFLOW_REPO` to the path of the repository root.

The Go binary targets `linux/arm64`, which matches the Astro CLI containers on Apple Silicon. On an Intel or AMD machine, run `ARCH=amd64 include/go_sdk/build.sh`. The Java jar and the TypeScript bundles don't depend on the architecture.

After building, run `astro dev restart`, then trigger the Dags tagged `multilang` and the three Dags in `dags/multilang/yaml/`.

## Git Dag bundle

`.env_example` configures a second Dag bundle, `dag-bundle-test`, that pulls Dags from the public [TJaniF/dag-bundle-test](https://github.com/TJaniF/dag-bundle-test) repository using the `git_default` connection. The repository is public, so the connection needs no token. Remove the bundle from `AIRFLOW__DAG_PROCESSOR__DAG_BUNDLE_CONFIG_LIST` if you don't want it.
