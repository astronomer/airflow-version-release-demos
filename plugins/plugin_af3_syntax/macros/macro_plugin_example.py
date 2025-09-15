from airflow.plugins_manager import AirflowPlugin
from datetime import datetime

# Will show up in templates through {{ macros.test_plugin.month_start(ds) }}
def month_start(ds):
    d = datetime.strptime(ds, "%Y-%m-%d")
    return d.replace(day=1).strftime("%Y-%m-%d")


class AirflowTestPlugin(AirflowPlugin):
    name = "macro_plugin_example"
    macros = [month_start]
