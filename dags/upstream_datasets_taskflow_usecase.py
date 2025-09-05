"""
### Create Airflow Datasets based on information in S3

This DAG lists all folders in an S3 bucket fitting a certain prefix and creates a new Airflow Dataset for each folder.
"""

from airflow import Dataset
from airflow.decorators import dag, task
from pendulum import datetime
from airflow.providers.amazon.aws.operators.s3 import (
    S3ListPrefixesOperator,
    S3CreateObjectOperator,
)

MY_S3_BUCKET = "myexamplebucketone"
MY_S3_FOLDER_PREFIX = "e"
MY_S3_BUCKET_DELIMITER = "/"
MY_DATA = "Hi S3 bucket!"
MY_FILENAME = "my_message.txt"
AWS_CONN_ID = "aws_conn"


@dag(
    dag_id="upstream_datasets_taskflow_usecase",
    start_date=datetime(2022, 12, 1),
    schedule=None,
    catchup=False,
    tags=["datasets", "taskflow", "usecase"],
)
def upstream_datasets_taskflow_usecase():
    # list all root level folders in my S3 bucket that start with my prefix
    list_folders_in_bucket = S3ListPrefixesOperator(
        task_id="list_folders_in_bucket",
        aws_conn_id=AWS_CONN_ID,
        bucket=MY_S3_BUCKET,
        prefix=MY_S3_FOLDER_PREFIX,
        delimiter=MY_S3_BUCKET_DELIMITER,
    )

    # create a separate Dataset object for each of the folders
    @task
    def create_datasets_from_s3_folders(folder_list):
        datasets_lists = []
        for folder in folder_list:
            uri = f"s3://{MY_S3_BUCKET}{MY_S3_BUCKET_DELIMITER}{folder}{MY_FILENAME}"
            datasets_lists.append(Dataset(uri))

        print(f"These datasets were created: {datasets_lists}")

        # returning a list of Datasets (2.5 feature)
        return datasets_lists

    list_of_datasets = create_datasets_from_s3_folders(list_folders_in_bucket.output)

    # write MY_DATA into a new MY_FILENAME in each of the S3 folders
    write_file_to_S3 = S3CreateObjectOperator.partial(
        task_id="write_file_to_S3", aws_conn_id=AWS_CONN_ID, data=MY_DATA, replace=True
    ).expand(
        s3_key=list_of_datasets.map(
            lambda x: x.uri
        )  # retrieving the keys from the Datasets
    )

    # since outlets is not a mappable parameter, use a task flow task to produce to the datasets
    # this too is only possible in 2.5+
    @task
    def produce_to_datasets(dataset_obj):
        return dataset_obj

    write_file_to_S3 >> produce_to_datasets.expand(dataset_obj=list_of_datasets)


upstream_datasets_taskflow_usecase()