from __future__ import annotations

import asyncio
import time
from asgiref.sync import sync_to_async
from typing import TYPE_CHECKING, Any, Sequence, cast, AsyncIterator

from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.models.baseoperator import BaseOperator
from airflow.sdk import ResumableJobMixin
from airflow.triggers.base import BaseTrigger, TriggerEvent
from pendulum import from_timestamp

from openai import OpenAI

XCOM_FINE_TUNE_JOB_ID = "fine_tune_job_id"
XCOM_FINE_TUNE_MODEL_NAME = "fine_tune_model"

if TYPE_CHECKING:

    from airflow.models.taskinstancekey import TaskInstanceKey
    from airflow.utils.context import Context




class OpenAIFineTuneTrigger(BaseTrigger):
    """
    Waits asynchronously for a Fine-tuning job on OpenAI to complete.

    :param fine_tune_job_id: The ID of the fine-tuning job.
    :openai_api_key: The OpenAI API key.
        If not provided, it will be fetched from the environment variable OPENAI_API_KEY.
    :poll_interval: The interval at which to poll the OpenAI API for the job status.
    """

    def __init__(
        self,
        fine_tune_job_id: str,
        openai_api_key: str = None,
        poll_interval: float = 5.0,
    ):
        super().__init__()
        self.fine_tune_job_id = fine_tune_job_id
        self.openai_api_key = openai_api_key
        self.poll_interval = poll_interval

    def serialize(self) -> tuple[str, dict[str, Any]]:
        """Serialize OpenAIFineTuneTrigger arguments and classpath."""
        return (
            "include.custom_operators.gpt_fine_tune.OpenAIFineTuneTrigger",
            {
                "fine_tune_job_id": self.fine_tune_job_id,
                "openai_api_key": self.openai_api_key,
                "poll_interval": self.poll_interval,
            },
        )

    async def run(self) -> AsyncIterator[TriggerEvent]:
        """Check periodically if the dag run exists, and has hit one of the states yet, or not."""
        while True:
            fine_tune_info = await self.get_fine_tune_job_info()
            if fine_tune_info.status == "succeeded":
                self.log.info("Fine-tuning job completed successfully.")
                yield TriggerEvent(self.serialize())
                return
            if fine_tune_info.status == "failed":
                self.log.error("Fine-tuning job failed.")
                yield TriggerEvent(self.serialize())
                return
            if fine_tune_info.status == "cancelled":
                self.log.info("Fine-tuning job was cancelled.")
                yield TriggerEvent(self.serialize())
                return
            self.log.info(
                f"Fine-tuning job status: {fine_tune_info.status}. Trigger sleeping for {self.poll_interval} seconds."
            )
            await asyncio.sleep(self.poll_interval)

    @sync_to_async
    def get_fine_tune_job_info(self) -> str:
        """Get the status of the fine-tuning job."""

        if self.openai_api_key:
            client = OpenAI(api_key=self.openai_api_key)
        else:
            client = (
                OpenAI()
            )  # if no key is provided, attempt to fetch from the env OPEN_AI_API_KEY

        fine_tune_info = client.fine_tuning.jobs.retrieve(self.fine_tune_job_id)

        return fine_tune_info


class OpenAIFineTuneOperator(ResumableJobMixin, BaseOperator):
    """
    Fine tunes a model on OpenAI.

    :param fine_tuning_file_id: The ID of training examples file for fine-tuning.
    :param validation_file_id: The ID of the validation examples file.
    :param openai_api_key: The OpenAI API key.
        If not provided, it will be fetched from the environment variable OPENAI_API_KEY.
    :param model: The model to fine-tune (default: gpt-3.5-turbo).
    :param suffix: A suffix to append to the fine-tuned model name.
        If not provided, the logical date timestamp will be used. (default: None)
    :param wait_for_completion: Whether to wait for the fine-tuning job to complete. (default: False)
    :param poke_interval: The interval at which to poll the OpenAI API for the job status. (default: 60)
    :param deferrable: Whether to use deferrable mode. (default: False)
    """

    template_fields: Sequence[str] = (
        "fine_tuning_file_id",
        "validation_file_id",
        "openai_api_key",
        "model",
        "suffix",
        "wait_for_completion",
        "poke_interval",
    )
    template_fields_renderers = {"conf": "py"}
    ui_color = "#73deff"

    # task_state_store key the mixin persists the fine-tune job id under (crash recovery)
    external_id_key = XCOM_FINE_TUNE_JOB_ID

    def __init__(
        self,
        *,
        fine_tuning_file_id: str,
        validation_file_id: str,
        openai_api_key: str = None,
        model: str = "gpt-3.5-turbo",
        suffix: str = None,
        wait_for_completion: bool = False,
        poke_interval: int = 60,
        deferrable: bool = conf.getboolean(
            "operators", "default_deferrable", fallback=False
        ),
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.fine_tuning_file_id = fine_tuning_file_id
        self.validation_file_id = validation_file_id
        self.openai_api_key = openai_api_key
        self.model = model
        self.suffix = suffix
        self.wait_for_completion = wait_for_completion
        self.poke_interval = poke_interval
        self._defer = deferrable

    def execute(self, context: Context):
        # Synchronous wait path is crash-safe via ResumableJobMixin: the fine-tune job id is
        # persisted to task_state_store, so a retry reconnects to the running job instead of
        # kicking off a duplicate (and billable) fine-tune. The deferrable path is unchanged.
        if self.wait_for_completion and not self._defer:
            return self.execute_resumable(context)

        client = self._client()
        self.suffix = self.suffix or context["ts_nodash"]

        fine_tune_info = client.fine_tuning.jobs.create(
            training_file=self.fine_tuning_file_id,
            validation_file=self.validation_file_id,
            model=self.model,
            suffix=self.suffix,
        )
        self.fine_tune_job_id = fine_tune_info.id
        self.fine_tune_model_name = fine_tune_info.fine_tuned_model
        self.log.info(f"Fine-tuning job created. Job ID: {self.fine_tune_job_id}")
        context["task_instance"].xcom_push(
            key=XCOM_FINE_TUNE_JOB_ID, value=self.fine_tune_job_id
        )

        if self.wait_for_completion:  # deferrable; the sync wait path returned above
            self.log.info(
                f"Deferring the task of checking for the status of Fine-tuning job: {self.fine_tune_job_id}"
            )
            self.defer(
                trigger=OpenAIFineTuneTrigger(
                    fine_tune_job_id=self.fine_tune_job_id,
                    openai_api_key=self.openai_api_key,
                    poll_interval=self.poke_interval,
                ),
                method_name="execute_complete",
            )
        else:
            self.log.info(
                f"Fine-tuning job {self.fine_tune_job_id} was kicked off. Not waiting for completion."
                + "Set wait_for_completion=True to wait for completion."
            )

    # --- ResumableJobMixin hooks: drive the synchronous, non-deferrable wait path ---

    def submit_job(self, context: Context):
        client = self._client()
        self.suffix = self.suffix or context["ts_nodash"]
        fine_tune_info = client.fine_tuning.jobs.create(
            training_file=self.fine_tuning_file_id,
            validation_file=self.validation_file_id,
            model=self.model,
            suffix=self.suffix,
        )
        self.fine_tune_job_id = fine_tune_info.id
        self.fine_tune_model_name = fine_tune_info.fine_tuned_model
        self.log.info(f"Fine-tuning job created. Job ID: {self.fine_tune_job_id}")
        context["task_instance"].xcom_push(
            key=XCOM_FINE_TUNE_JOB_ID, value=self.fine_tune_job_id
        )
        return self.fine_tune_job_id

    def get_job_status(self, external_id, context: Context) -> str:
        return self._client().fine_tuning.jobs.retrieve(external_id).status

    def is_job_active(self, status: str) -> bool:
        return status in ("validating_files", "queued", "running")

    def is_job_succeeded(self, status: str) -> bool:
        return status == "succeeded"

    def poll_until_complete(self, external_id, context: Context) -> None:
        while True:
            status = self.get_job_status(external_id, context)
            if not self.is_job_active(status):
                break
            self.log.info(
                f"Waiting for fine-tuning job {external_id} to complete. "
                f"Status: {status}. Sleeping for {self.poke_interval} seconds."
            )
            time.sleep(self.poke_interval)
        if not self.is_job_succeeded(status):
            raise AirflowException(
                f"Fine-tuning job {external_id} ended in non-success state: {status}"
            )

    def get_job_result(self, external_id, context: Context):
        fine_tune_info = self._client().fine_tuning.jobs.retrieve(external_id)
        self.log_fine_tune_info(fine_tune_info, context)
        return fine_tune_info.result_files

    def _client(self) -> OpenAI:
        return OpenAI(api_key=self.openai_api_key) if self.openai_api_key else OpenAI()

    def execute_complete(self, context: Context, event: tuple[str, dict[str, Any]]):
        """Execute when the trigger is complete."""

        self.log.info("Trigger is complete.")
        self.log.info(f"Event: {event}")
        fine_tune_job_id = event[1]["fine_tune_job_id"]
        print(fine_tune_job_id)
        result_files = self.get_fine_tune_job_info(
            fine_tune_job_id=fine_tune_job_id, context=context
        )

        return result_files

    def get_fine_tune_job_info(self, fine_tune_job_id, context: Context) -> str:

        if self.openai_api_key:
            client = OpenAI(api_key=self.openai_api_key)
        else:
            client = (
                OpenAI()
            )  # if no key is provided, attempt to fetch from the env OPEN_AI_API_KEY

        fine_tune_info = client.fine_tuning.jobs.retrieve(fine_tune_job_id)

        self.log.info(f"Checked status of fine-tuning job {fine_tune_job_id}")

        if fine_tune_info.status == "queued":
            self.log.info(f"Fine-tuning job {fine_tune_job_id} is queued.")
        if fine_tune_info.status == "validating_files":
            self.log.info(f"Fine-tuning job {fine_tune_job_id} is validating files.")
        if fine_tune_info.status == "running":
            self.log.info(f"Fine-tuning job {fine_tune_job_id} is running.")
        if fine_tune_info.status == "succeeded":
            self.log_fine_tune_info(fine_tune_info, context)
            return fine_tune_info.result_files
        if fine_tune_info.status == "failed":
            raise AirflowException(
                f"Fine-tuning job {fine_tune_job_id} failed: "
                + f"Status: {fine_tune_info.error.code}"
                + f"{fine_tune_info.error.message}"
            )
        if fine_tune_info.status == "cancelled":
            raise AirflowException(f"Fine-tuning job {fine_tune_job_id} was cancelled.")

        AirflowException(
            f"Fine-tuning job {fine_tune_job_id} in unknown state {fine_tune_info.status}"
        )

    def log_fine_tune_info(self, fine_tune_info, context: Context):

        # compute duration
        fine_tuning_duration_seconds = (
            fine_tune_info.finished_at - fine_tune_info.created_at
        )
        fine_tuning_duration_hr = fine_tuning_duration_seconds // 3600
        fine_tuning_duration_min = (fine_tuning_duration_seconds % 3600) // 60
        fine_tuning_duration_s = (fine_tuning_duration_seconds % 3600) % 60

        # log fine tuning info
        self.log.info("Fine-tuning job completed successfully.")
        self.log.info("--- Fine-tuning Job Info ---")
        self.log.info(f"Fine-tuned model: {fine_tune_info.fine_tuned_model}")
        self.log.info(f"Model: {fine_tune_info.model}")
        self.log.info(f"Model ID: {fine_tune_info.id}")
        self.log.info(f"Organization ID: {fine_tune_info.organization_id}")
        self.log.info(f"Trained tokens: {fine_tune_info.trained_tokens}")
        self.log.info(f"Training file: {fine_tune_info.training_file}")
        self.log.info(
            f"Hyperparameters: {fine_tune_info.hyperparameters.n_epochs} epochs, "
            + f"batch size: {fine_tune_info.hyperparameters.batch_size}, "
            + f"learning rate multiplier: {fine_tune_info.hyperparameters.learning_rate_multiplier}"
        )
        self.log.info(f"Result file ids: {fine_tune_info.result_files}")

        self.log.info("--- Fine tuning Duration ---")
        self.log.info(f"Created at: {from_timestamp(fine_tune_info.created_at)}")
        self.log.info(f"Finished at: {from_timestamp(fine_tune_info.finished_at)}")
        self.log.info(
            f"Fine-tuning Duration: {fine_tuning_duration_hr} hr {fine_tuning_duration_min} min {fine_tuning_duration_s} s"
        )

        print(fine_tune_info.fine_tuned_model)

        context["ti"].xcom_push(XCOM_FINE_TUNE_MODEL_NAME, fine_tune_info.fine_tuned_model)