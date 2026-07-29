from airflow.sdk import dag
from airflow.providers.ssh.operators.ssh import SSHOperator
from pendulum import duration
import base64


class CustomSSHOperator(SSHOperator):

    template_fields = ("out_file", *SSHOperator.template_fields)

    def __init__(self, *, out_file, check_command, **kwargs):
        super().__init__(**kwargs)
        self.out_file = out_file
        self.check_command = check_command

    def execute(self, context):
        tss = context["task_state_store"]
        remote_pid = tss.get("remote_pid")

        if not remote_pid:
            remote_pid = base64.b64decode(super().execute(context)).decode().strip()
            tss.set("remote_pid", remote_pid)
            tss.set("remote_out_file", self.out_file)
            raise Exception(
                f"Simulated worker interruption right after launch. Remote PID {remote_pid} "
                "keeps running; the retry reconnects via the stored PID instead of relaunching."
            )

        out_file = tss.get("remote_out_file")
        self.log.info(f"Reconnecting to remote PID {remote_pid} from a previous attempt.")
        self.command = self.check_command.replace("{pid}", remote_pid).replace("{out_file}", out_file)
        return super().execute(context)


@dag(tags=["task state store"])
def task_state_store_traditional_op_example():

    CustomSSHOperator(
        task_id="my_ssh_task",
        ssh_conn_id="ssh_default",
        out_file="/tmp/tss_job_{{ run_id }}.out",
        command=(
            "nohup sh -c 'sleep 60; rc=$?; echo finished > {{ task.out_file }}; "
            "echo $rc > {{ task.out_file }}.rc' >/dev/null 2>&1 & echo $!"
        ),
        check_command=(
            "while kill -0 {pid} 2>/dev/null; do sleep 2; done; "
            "rc=$(cat {out_file}.rc 2>/dev/null); cat {out_file}; "
            "[ \"$rc\" = \"0\" ]"
        ),
        cmd_timeout=120,
        retries=1,
        retry_delay=duration(seconds=5),
    )


task_state_store_traditional_op_example()
