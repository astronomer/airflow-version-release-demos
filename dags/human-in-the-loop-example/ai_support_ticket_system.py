from airflow.providers.standard.operators.hitl import HITLBranchOperator, HITLEntryOperator
from airflow.sdk import dag, task, Param, chain
from datetime import timedelta
import random
from typing import Literal
from airflow_ai_sdk.models.base import BaseModel


class TicketResponse(BaseModel):
    summary: str
    response: str
    priority: Literal["low", "medium", "high"]
    confidence_score: float
    suggested_tags: list[str]


@dag
def ai_support_ticket_system():

    @task
    def fetch_pending_ticket() -> list[dict]:
        from include.custom_functions import get_open_tickets

        tickets = get_open_tickets(1)
        return tickets[0]

    _fetch_pending_ticket = fetch_pending_ticket()

    @task.llm(
        model="gpt-4o-mini",
        system_prompt="""
        You are friendly and helpful support agent generating answers to tickets.
        Make sure to address the customer by name in the response.
        """,
        output_type=TicketResponse,
    )
    def generate_ai_response(ticket: dict):
        import json

        ticket_str = json.dumps(ticket)
        return ticket_str

    _generate_ai_response = generate_ai_response(ticket=_fetch_pending_ticket)

    @task
    def format_approval_request(ai_response: dict, original_ticket: dict):
        return {
            "ticket_info": f"**Ticket:** {original_ticket['ticket_id']}\n**Customer:** {original_ticket['customer']}\n**Subject:** {original_ticket['subject']}\n**Priority:** {original_ticket['priority']}",
            "summary": ai_response["summary"],
            "ai_response": ai_response["response"],
            "confidence": ai_response["confidence_score"],
            "priority": ai_response["priority"],
            "suggested_tags": ai_response["suggested_tags"],
            "metadata": ai_response,
            "original_ticket": original_ticket,
        }

    _format_approval_request = format_approval_request(
        ai_response=_generate_ai_response, original_ticket=_fetch_pending_ticket
    )

    # Human approval step
    _review_ai_response = HITLBranchOperator(
        task_id="review_ai_response",
        subject="🎫 AI Support Response Ready for Review",
        body="""**Please review the AI-generated support ticket response below:**

{{ ti.xcom_pull(task_ids='format_approval_request')['ticket_info'] }}

**AI Summary:**
{{ ti.xcom_pull(task_ids='format_approval_request')['summary'] }}

**AI Suggested Priority:** {{ ti.xcom_pull(task_ids='format_approval_request')['priority'] }}
**AI Confidence:** {{ "%.0f" | format(ti.xcom_pull(task_ids='format_approval_request')['confidence'] * 100) }}%
**Suggested Tags:** {{ ti.xcom_pull(task_ids='format_approval_request')['suggested_tags'] | join(', ') }}

**AI Response:**
```
{{ ti.xcom_pull(task_ids='format_approval_request')['ai_response'] }}
```

**Instructions:**
- **Approve**: Send this response to the customer
- **Reject**: Route to human agent for manual response

Please review for accuracy, tone, and completeness.""",
        options=["Approve AI Response", "Respond Manually", "Escalate To CRE", "Escalate To CSM"],
        options_mapping={
            "Approve AI Response": "approve_ai_response",
            "Respond Manually": "respond_manually",
            "Escalate To CRE": "escalate_to_cre",
            "Escalate To CSM": "escalate_to_csm",
        },
        defaults=["Escalate To CSM"],
        multiple=True,
        execution_timeout=timedelta(hours=4),
    )

    @task
    def approve_ai_response(original_ticket: dict, ai_response: dict):

        print("Processing ticket:", original_ticket["ticket_id"])
        print("Sending Approved AI Response to customer:", ai_response["ai_response"])

    _approve_ai_response = approve_ai_response(
        ai_response=_format_approval_request,
        original_ticket=_fetch_pending_ticket,
    )

    _respond_manually = HITLEntryOperator(
        task_id="respond_manually",
        subject="🎫 Manual Response",
        body="""**Please enter the manual response to the customer:**
        ```
        {{ ti.xcom_pull(task_ids='format_approval_request')['original_ticket']['message'] }}
        ```
        """,
        params={
            "manual_response": Param(
                "None",
                type=["string"],
            ),
        },
    )

    @task
    def process_manual_response(original_ticket: dict, manual_response: str):
        print("Processing ticket:", original_ticket["ticket_id"])
        print("Sending Manual Response to customer:", manual_response["params_input"]["manual_response"])

    _process_manual_response = process_manual_response(
        original_ticket=_fetch_pending_ticket,
        manual_response=_respond_manually.output,
    )

    @task
    def escalate_to_cre(original_ticket: dict):
        print("Processing ticket:", original_ticket["ticket_id"])
        print("Escalating to CRE")

    _escalate_to_cre = escalate_to_cre(
        original_ticket=_fetch_pending_ticket,
    )

    @task
    def escalate_to_csm(original_ticket: dict):

        print("Processing ticket:", original_ticket["ticket_id"])
        print("Escalating to CSM")

    _escalate_to_csm = escalate_to_csm(
        original_ticket=_fetch_pending_ticket,
    )

    chain(
        _format_approval_request,
        _review_ai_response,
        [_approve_ai_response, _respond_manually, _escalate_to_cre, _escalate_to_csm],
    )
    chain(
        _respond_manually,
        _process_manual_response,
    )


ai_support_ticket_system()