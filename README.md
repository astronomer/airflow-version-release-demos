# Apache Airflow 3.2 Example Dags

This repository contains example Dags showcasing features and improvements introduced in Apache Airflow 3.2. And shown in the [Introducing Apache Airflow® 3.2](https://www.astronomer.io/events/webinars/introducing-airflow-3-2-video) webinar.

# How to use this repository

This section explains how to run this repository with Airflow.

## Steps to run this repository

Download the [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) to run Airflow locally in containers. `astro` is the only package you will need to install.

1. Run `git clone https://github.com/astronomer/airflow-version-release-demos.git` on your computer to create a local clone of this repository.
2. Check out the `v3.2` branch: `git checkout v3.2`.
3. Install the Astro CLI by following the steps in the [Astro CLI documentation](https://www.astronomer.io/docs/astro/cli/install-cli).
4. Run `astro dev start` in your cloned repository.
5. After your Astro project has started, view the Airflow UI at `localhost:8080`.

## Theming

Airflow 3.2 supports UI theming via the `AIRFLOW__API__THEME` environment variable. The `airflow_themes` folder contains sample `.env` files with pre-built themes you can try:

- **`.env_example_simple_theme`** — A minimal color rebranding example.
- **`.env_example_dracula`** — A Dracula-inspired dark theme.
- **`.env_example_lcars`** — An LCARS (Star Trek) inspired theme.
- **`.env_example_severance`** — A Severance-inspired theme.

To use a theme, copy the contents of one of these files into your `.env` file and restart Airflow (`astro dev restart`).

A **Theme Explorer** plugin is also included in the `plugins/theme_explorer` directory. It provides a custom UI page in Airflow for exploring and previewing theme tokens. You can access the plugin under **Browse** > **Theme Explorer**.

## Useful links

- [Apache Airflow® release notes](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html).
- [Assets guide](https://docs.astronomer.io/learn/airflow-datasets).
- [Async guide](https://docs.astronomer.io/learn/deferrable-operators).
- [Airflow Config reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html).

# Project Structure

This repository contains the following files and folders:

- `.astro`: files necessary for Astro CLI commands.
- `dags`: all Dags in your Airflow environment. Organized into subfolders by feature area:
  - `assets_basics`: basic asset scheduling and inlet/outlet examples.
  - `assets_partitions`: partitioned assets, composite partition keys, partition mappers, and domino (chained) Dags.
  - `async`: async Python operators, the async task decorator, and deferrable operators.
  - `other`: miscellaneous Dags including deadline alerts, HITL workflows, manual-run restrictions, and UI showcase.
- `airflow_themes`: sample `.env` files with pre-built Airflow UI themes.
- `api_scripts`: an example script for triggering Dags with partition keys.
- `include`: supporting files included in the Airflow environment (callback functions, custom deferrable operator).
- `plugins`: Airflow plugins, including the Theme Explorer plugin.
- `tests`: folder for Dag tests.
- `.env`: environment variables for theming and configuration (not committed, see `airflow_themes` for examples).
- `Dockerfile`: the Dockerfile using the Astro CLI with Astro Runtime 3.2.
- `packages.txt`: system-level packages installed in the Airflow environment.
- `README.md`: this file.
- `requirements.txt`: Python packages installed in the Airflow environment.
