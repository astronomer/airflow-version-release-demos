# Apache Airflow 3.4 Example Dags

This repository contains example Dags and plugins showcasing features and improvements introduced in Apache Airflow 3.4. The project runs on the pre-release Astro Runtime image `runtime-dev:3.4-1-alpha3`.

# How to use this repository

Download the [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) to run Airflow locally in containers. `astro` is the only package you need to install for the Python Dags.

1. Run `git clone https://github.com/astronomer/airflow-version-release-demos.git` on your computer to create a local clone of this repository.
2. Check out the `v3.4` branch: `git checkout v3.4`.
3. Install the Astro CLI by following the steps in the [Astro CLI documentation](https://www.astronomer.io/docs/astro/cli/install-cli).
4. Rename the `.env_example` file to `.env`. If you want to run any of the AI-related Dags, replace the `<your key>` placeholders with your AI API key.
5. Run `astro dev start` in your cloned repository.
6. After your Astro project has started, view the Airflow UI at `localhost:8080`.

## What's in this repository

| Folder | What it shows |
|---|---|
| `dags/task_loops/` | Task loops: repeat a task or task group until a condition is met. `basic/` has small loops (doubling, Fibonacci, draining a list, `until` with params or upstream values), `advanced/` has agent and human-in-the-loop loops, and `experiments/` covers edge cases such as loops with mapping, nested task groups and retries. |
| `dags/retry_policies/` | Retry policies: decide per exception whether a task retries, fails or reschedules, including `ExceptionRetryPolicy`, `ChainRetryPolicy` and the AI retry policies from the common AI provider. |
| `dags/common_ai/` | Features of the [common AI provider](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/index.html), starting with tool approval for an agent (`agent_tool_approval`). |
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

The Dags in `dags/common_ai/`, `ai_retry_policies.py` and `chain_retry_policy.py` in `dags/retry_policies/`, and `agent_support_reply.py` and `agent_text_to_sql.py` in `dags/task_loops/advanced/` use the `pydanticai_default` connection from `.env`. Add your API key to it.

The common AI provider adds an **AI Model** tab to the task instances of LLM and agent tasks, showing the model, token usage and cost. Two known issues:

- The tab only works when you open the UI at `localhost:8080`. Through the Astro CLI's proxy URL (`<project>.localhost:6563`), the tab stays empty because the browser blocks the plugin's bundle.
- The tab shows "Select a region and index for this task instance" for tasks inside a task loop.

## Run the multi-language Dags

`dags/multilang/` contains one ETL pipeline in several languages:

- `python_baseline_etl.py` is plain Python and runs without extra steps.
- `yaml/yaml_etl.yaml` and `yaml/yaml_etl_python.yaml` are YAML Dags. They need the `AIRFLOW__DAG_PROCESSOR__DAG_IMPORTER_CONFIGS` line from `.env_example`.
- `go/main.go`, `java/JavaEtl.java` and `typescript/typescript_etl.ts` are native Go, Java and TypeScript Dags.
- `<language>_stub_etl.py` are Python Dags whose transform step runs in Go, Java or TypeScript with `@task.stub`. `polyglot_etl.py` runs extract in Go, transform in Java and load in TypeScript.
- `yaml/yaml_etl_typescript.yaml` is a YAML Dag with a TypeScript task.

The native Dags and the stub tasks need compiled artifacts, which are not committed. Their handlers are in the same artifact as each language's native Dag, so one build per language covers both. The coordinator settings (`AIRFLOW__SDK__COORDINATORS` and `AIRFLOW__SDK__QUEUE_TO_COORDINATOR`) are in `.env_example`, and the Dockerfile and `packages.txt` already add Node and a Java runtime to the image.

The build scripts run in Docker, so you don't need Go, a JDK or Node installed locally. The language SDKs are not published yet, so the scripts build them from a local clone of [apache/airflow](https://github.com/apache/airflow):

```bash
git clone https://github.com/apache/airflow.git ~/code/apache/airflow

include/go_sdk/build.sh
include/java_sdk/build.sh
include/typescript_sdk/build.sh
```

Each script writes its artifact next to the Dag source: `dags/multilang/go/go_etl`, `dags/multilang/java/java_etl.jar`, and `*.min.mjs` files in `dags/multilang/typescript/` and `dags/multilang/yaml/`. If your clone is somewhere else, set `GO_SDK_DIR` (path to `go-sdk`), `AIRFLOW_REPO` (path to the repository root, for Java) or `TS_SDK_DIR` (path to `ts-sdk`).

The Go and Java builds target `linux/arm64`, which matches the Astro CLI containers on Apple Silicon. On an Intel or AMD machine, change `arm64` to `amd64` in `include/go_sdk/build.sh` (both `--platform` and `--goarch`). The Java jar is architecture-neutral, so only the `--platform` flag of its build container changes.

After building, run `astro dev restart`, then trigger the Dags tagged `multilang`.

## Git Dag bundle

`.env_example` configures a second Dag bundle, `dag-bundle-test`, that pulls Dags from the public [TJaniF/dag-bundle-test](https://github.com/TJaniF/dag-bundle-test) repository using the `git_default` connection. The repository is public, so the connection needs no token. Remove the bundle from `AIRFLOW__DAG_PROCESSOR__DAG_BUNDLE_CONFIG_LIST` if you don't want it.
