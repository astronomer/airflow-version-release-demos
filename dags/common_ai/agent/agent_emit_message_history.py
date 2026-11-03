"""
## Agent emit message history

`emit_message_history=True` pushes the agent's full transcript to XCom under
the key `message_history`, without seeding the run with an earlier
conversation. Use it to record what the agent did, for auditing or for a
follow-up turn in a later task. New in Common AI 1.1.
"""

import json

from airflow.sdk import dag, task


@dag(tags=["common_ai"])
def agent_emit_message_history():
    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="You are a dispatcher. Answer in one sentence.",
        emit_message_history=True,
    )
    def answer():
        return "Which is closer to Earth on average, Mars or Venus?"

    @task
    def print_transcript(ti=None):
        transcript = ti.xcom_pull(task_ids="answer", key="message_history")
        messages = json.loads(transcript) if isinstance(transcript, (str, bytes)) else transcript
        print(f"The transcript has {len(messages)} messages:")
        for message in messages:
            print(f"  {message.get('kind')}: {[part.get('part_kind') for part in message.get('parts', [])]}")

    answer() >> print_transcript()


agent_emit_message_history()
