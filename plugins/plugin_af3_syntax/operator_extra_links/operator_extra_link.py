from airflow.plugins_manager import AirflowPlugin
from airflow.sdk.bases.operatorlink import BaseOperatorLink
from airflow.models import XCom
from urllib.parse import quote_plus
from typing import Optional, Dict, Any


class GoogleSearchXComLink(BaseOperatorLink):
    name = "🔍 Search Return Value in Google"

    def get_link(self, operator, *, ti_key, **context) -> str:

        xcom_value = XCom.get_value(ti_key=ti_key, key="return_value")

        search_term = str(xcom_value)
        encoded_search = quote_plus(search_term)

        return f"https://www.google.com/search?q={encoded_search}"


class OperatorExtraLinkPlugin(AirflowPlugin):
    name = "operator_extra_link"
    operator_extra_links = [GoogleSearchXComLink()]
