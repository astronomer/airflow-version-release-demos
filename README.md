# Apache Airflow 3.3 Example Dags

This repository contains example Dags showcasing features and improvements introduced in Apache Airflow 3.3. 

# How to use this repository

Download the [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) to run Airflow locally in containers. `astro` is the only package you will need to install.

1. Run `git clone https://github.com/astronomer/airflow-version-release-demos.git` on your computer to create a local clone of this repository.
2. Check out the `v3.3` branch: `git checkout v3.3`.
3. Install the Astro CLI by following the steps in the [Astro CLI documentation](https://www.astronomer.io/docs/astro/cli/install-cli).
4. Rename the `.env_example` file to `.env`. If you want to run any of the AI-related Dags, you need to provide your AI API Key replacing the placeholders.
5. Run `astro dev start` in your cloned repository.
6. After your Astro project has started, view the Airflow UI at `localhost:8080`.

## Run the Go SDK Dag

`go_task_syntax_example` (`dags/go_sdk/`) runs one task in Go. You need to build the the Go source (`include/go_bundle/`) and copy the `AIRFLOW__SDK__COORDINATORS` and `AIRFLOW__SDK__QUEUE_TO_COORDINATOR` values from `.env_example` to `.env`.

Extra steps, after the steps above setup:

1. Install [Go](https://go.dev/dl/) 1.24+.
2. Build the Go bundle for the Linux Airflow container:
   ```
   cd include/go_bundle
   go tool airflow-go-pack --goos linux --goarch arm64 --output ./bin/go_task_syntax_example .
   ```
   Use `--goarch arm64` on Apple Silicon, `--goarch amd64` on Intel/AMD.
3. Run `astro dev restart`, then trigger the `go_task_syntax_example` Dag.

## Run the Java SDK Dag

`java_task_syntax_example` (`dags/java_sdk/`) runs one task in Java. You need to build the Java bundle (`include/java_sdk/`) and copy the `AIRFLOW__SDK__COORDINATORS` and `AIRFLOW__SDK__QUEUE_TO_COORDINATOR` values from `.env_example` to `.env`.

Extra steps, after the steps above setup:

1. Build the Java bundle. This uses a Gradle Docker image, so no local JDK or Gradle is needed:
   ```
   docker run --rm -v "$PWD/include/java_sdk":/home/gradle/project -v airflow_java_sdk_gradle_cache:/home/gradle/.gradle -w /home/gradle/project gradle:8.14-jdk21 gradle --no-daemon bundle
   cp include/java_sdk/build/bundle/*.jar include/java_bundle/
   ```
   The jar is plain JVM bytecode, so the same build works on Apple Silicon and Intel/AMD.
2. Run `astro dev restart`, then trigger the `java_task_syntax_example` Dag.