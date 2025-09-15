from airflow.plugins_manager import AirflowPlugin


class SimpleExternalViewPlugin(AirflowPlugin):
    name = "simple_external_view"

    external_views = [
        {

            "name": "Airflow Guides",
            "href": "https://www.astronomer.io/docs/learn",
            "destination": "dag",
            "url_route": "airflow_guides"
        }
    ]
