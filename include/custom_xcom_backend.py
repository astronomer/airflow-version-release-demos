import json

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk.bases.xcom import BaseXCom


class MyCustomXComBackend(BaseXCom):
    # the prefix is optional and used to make it easier to recognize
    # which reference strings in the Airflow metadata database
    # refer to an XCom that has been stored in remote storage
    PREFIX = "s3_and_gs://"
    S3_BUCKET_NAME = "s3-xcom-backend-example"
    GS_BUCKET_NAME = "gcs-xcom-backend-example"

    @classmethod
    def store_value(cls, coordinate, key, value):
        # make sure the value is JSON-serializable
        try:
            serialized_value = json.dumps(value)
        except TypeError as e:
            raise ValueError(f"XCom value is not JSON-serializable!: {e}")

        # build a storage path that is unique for each task instance,
        # including each iteration of a task inside a task loop
        object_key = coordinate.build_path(prefix="xcoms", key=key, suffix=".json")

        # the connection to AWS is created by using the S3 hook
        S3Hook(aws_conn_id="my_aws_conn_id").load_string(
            string_data=serialized_value,
            key=object_key,
            bucket_name=cls.S3_BUCKET_NAME,
            replace=True,
        )

        # the connection to GCS is created by using the GCS hook
        GCSHook(gcp_conn_id="my_gcs_conn_id").upload(
            bucket_name=cls.GS_BUCKET_NAME,
            object_name=object_key,
            data=serialized_value,
        )

        # the returned reference string is saved to the Airflow metadata
        # database and passed to load_value when the XCom is read
        return cls.PREFIX + object_key

    @classmethod
    def load_value(cls, stored):
        # if the stored XCom value doesn't start with the prefix,
        # read it the default way
        if not (isinstance(stored, str) and stored.startswith(cls.PREFIX)):
            return super().load_value(stored)

        object_key = stored.removeprefix(cls.PREFIX)
        hook = S3Hook(aws_conn_id="my_aws_conn_id")
        return json.loads(hook.read_key(key=object_key, bucket_name=cls.S3_BUCKET_NAME))
