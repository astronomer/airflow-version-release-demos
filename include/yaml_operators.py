from importlib import import_module

from airflow.providers.standard.operators.python import PythonOperator


class ImportStringPythonOperator(PythonOperator):
    def __init__(self, *, python_callable, **kwargs):
        if isinstance(python_callable, str):
            module_path, _, name = python_callable.rpartition(".")
            python_callable = getattr(import_module(module_path), name)
        super().__init__(python_callable=python_callable, **kwargs)
