from pathlib import Path

from airflow.plugins_manager import AirflowPlugin


class KlingonUIPlugin(AirflowPlugin):
    name = "klingon_ui"
    ui_translations = [Path(__file__).parent / "klingon_locales"]
