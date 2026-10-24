from airflow.plugins_manager import AirflowPlugin


class FailedDagsLabelPlugin(AirflowPlugin):
    name = "failed_dags_label"
    ui_translations = [
        {"en": {"dashboard": {"stats": {"failedDags": "Dags that need a hug"}}}},
    ]
