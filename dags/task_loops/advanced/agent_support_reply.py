from datetime import timedelta
from typing import Literal

from pydantic import BaseModel

from airflow.providers.standard.operators.hitl import HITLOperator
from airflow.sdk import Param, chain, dag, task, task_group

MAX_DRAFTS = 5

TICKET = {
    "ticket_id": "T-1042",
    "customer": "Benjamin Sisko",
    "subject": "Charged twice for my annual plan",
    "message": (
        "Hi, I upgraded to the annual plan yesterday and my card was charged twice ($240 each). "
        "I only want one plan. Can you refund the extra charge? This is pretty frustrating."
    ),
}


class TicketResponse(BaseModel):
    summary: str
    response: str
    priority: Literal["low", "medium", "high"]
    confidence_score: float
    suggested_tags: list[str]


def review_finished(*, loop):
    return loop.result["decision"] != "Request changes"


@dag(tags=["task_loop", "webinar"])
def agent_support_reply():

    @task
    def fetch_ticket():
        return TICKET

    @task_group
    def draft_support_reply(ticket):
        @task
        def gather_feedback(ticket, *, loop):
            if loop.index == 0:
                return {"ticket": ticket, "feedback": "", "previous_response": ""}
            return {
                "ticket": ticket,
                "feedback": loop.previous["feedback"],
                "previous_response": loop.previous["draft"].response,
            }

        @task.agent(
            llm_conn_id="pydanticai_default",
            system_prompt=(
                "You are a friendly and helpful support agent for a software company. "
                "Write a reply to the customer's ticket and address the customer by name."
            ),
            output_type=TicketResponse,
        )
        def draft_reply(context):
            ticket = context["ticket"]
            prompt = (
                f"Ticket {ticket['ticket_id']} from {ticket['customer']}\n"
                f"Subject: {ticket['subject']}\n\n{ticket['message']}"
            )
            if context["feedback"]:
                prompt += (
                    f"\n\nYour previous reply was:\n{context['previous_response']}"
                    f"\n\nThe reviewer asked for these changes:\n{context['feedback']}"
                )
            return prompt

        _gather_feedback = gather_feedback(ticket)
        _draft_reply = draft_reply(_gather_feedback)

        _review_reply = HITLOperator(
            task_id="review_reply",
            subject="AI support reply ready for review",
            body="""{% set draft = ti.xcom_pull(task_ids='draft_support_reply.draft_reply') %}
**Summary:** {{ draft.summary }}

**Suggested priority:** {{ draft.priority }}
**Confidence:** {{ "%.0f" | format(draft.confidence_score * 100) }}%
**Suggested tags:** {{ draft.suggested_tags | join(', ') }}

**Reply:**
```
{{ draft.response }}
```

- **Approve**: send this reply to the customer.
- **Request changes**: write your feedback below, the agent drafts a new reply.
- **Escalate to CRE**: hand the ticket to a human engineer.""",
            options=["Approve", "Request changes", "Escalate to CRE"],
            defaults="Escalate to CRE",
            params={"feedback": Param(None, type=["null", "string"], description="What should change?")},
            response_timeout=timedelta(hours=4),
        )

        @task
        def record_review(draft, review):
            decision = review["chosen_options"][0]
            feedback = review["params_input"].get("feedback") or ""
            print(f"Decision: {decision}\nFeedback: {feedback or 'none'}")
            return {"draft": draft, "decision": decision, "feedback": feedback}

        chain(_draft_reply, _review_reply)
        record_review(_draft_reply, _review_reply.output)

    @task
    def handle_ticket(ticket, reviews):
        final = reviews[-1]
        if final["decision"] == "Approve":
            print(f"Sending reply to {ticket['customer']} after {len(reviews)} draft(s):\n{final['draft'].response}")
        else:
            print(f"Escalating ticket {ticket['ticket_id']} to CRE after {len(reviews)} draft(s).")

    _fetch_ticket = fetch_ticket()

    _draft_support_reply = draft_support_reply.partial(ticket=_fetch_ticket).loop(
        max_iterations=MAX_DRAFTS, until=review_finished
    )

    _handle_ticket = handle_ticket(_fetch_ticket, _draft_support_reply["record_review"].output)


agent_support_reply()
