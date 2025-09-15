from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
from plugins.plugin_af3_syntax.operator_extra_links.operator_extra_link import (
    GoogleSearchXComLink,
)


class SearchBashOperator(BashOperator):
    operator_extra_links = [GoogleSearchXComLink()]


@dag
def plugin_dag():
    macro_task = BashOperator(
        task_id="print_hello",
        bash_command="echo {{ macros.macro_plugin_example.month_start(ds) }}",
    )

    search_task = SearchBashOperator(
        task_id="search_task",
        bash_command="echo 'Cute animal picture'",
    )

    macro_task >> search_task


plugin_dag()
