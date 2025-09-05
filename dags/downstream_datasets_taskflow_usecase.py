"""
### Copy all files from one S3 bucket to another using dynamic task mapping

This DAG lists all existing files in a folder in an S3 bucket and dynamically copies them to another
S3 bucket using .map and .expand_kwargs.
"""

from airflow import Dataset
from airflow.decorators import dag
from pendulum import datetime
from airflow.providers.amazon.aws.operators.s3 import (
    S3ListOperator,
    S3CopyObjectOperator,
)

MY_S3_BUCKET = "myexamplebucketone"
MY_FIRST_FOLDER = "ex1/"
MY_S3_BUCKET_DELIMITER = "/"
MY_FILENAME = "my_message.txt"
AWS_CONN_ID = "aws_conn"

MY_S3_BUCKET_TO_COPY_TO = "myexamplebuckettwo"

my_dataset = Dataset(
    f"s3://{MY_S3_BUCKET}{MY_S3_BUCKET_DELIMITER}{MY_FIRST_FOLDER}{MY_FILENAME}"
)


@dag(
    dag_id="downstream_datasets_taskflow_usecase",
    start_date=datetime(2022, 12, 1),
    schedule=[my_dataset],
    catchup=False,
    tags=["datasets", "taskflow", "usecase"],
)
def downstream_datasets_taskflow_usecase():
    # list all existing files in MY_FIRST_FOLDER in MY_S3_BUCKET
    list_files = S3ListOperator(
        task_id=f"list_files",
        aws_conn_id=AWS_CONN_ID,
        bucket=MY_S3_BUCKET,
        prefix=MY_FIRST_FOLDER,
        delimiter=MY_S3_BUCKET_DELIMITER,
    )

    # copy all files to MY_S3_BUCKET_TO_COPY_TO
    copy_files = S3CopyObjectOperator.partial(
        task_id="copy_files",
        aws_conn_id=AWS_CONN_ID,
    ).expand_kwargs(
        list_files.output.map(
            lambda x: {
                "source_bucket_key": f"s3://{MY_S3_BUCKET}{MY_S3_BUCKET_DELIMITER}{x}",
                "dest_bucket_key": f"s3://{MY_S3_BUCKET_TO_COPY_TO}{MY_S3_BUCKET_DELIMITER}{x}",
            }
        )
    )

    list_files >> copy_files


downstream_datasets_taskflow_usecase()
