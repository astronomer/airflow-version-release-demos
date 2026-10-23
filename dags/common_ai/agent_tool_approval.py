"""
## Agent tool approval

The agent can look up orders freely, but every call to `refund_order` pauses the task
and asks for approval on the Required Actions page. The task's output is the agent's
final `Resolution`; nobody reviews that answer.
"""

from datetime import timedelta

from pydantic import BaseModel
from pydantic_ai.toolsets.function import FunctionToolset

from airflow.sdk import dag, task

ORDERS = {
    7: {"total": 42, "status": "carrier marked it lost"},
    8: {"total": 120, "status": "carrier marked it lost"},
}


def lookup_order(order_id: int) -> str:
    """Look up an order's total and delivery status."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"order {order_id} does not exist"
    return f"order {order_id}: ${order['total']}, {order['status']}"


def refund_order(order_id: int, amount: float) -> str:
    """Refund an order. Irreversible."""
    print(f"Refunding ${amount} for order {order_id}")
    return f"refunded ${amount} for order {order_id}"


class Resolution(BaseModel):
    refunded_orders: list[int]
    reply_to_customer: str


shop = FunctionToolset(tools=[lookup_order, refund_order]).approval_required(
    lambda ctx, tool_def, args: tool_def.name == "refund_order"
)


@dag(tags=["common_ai"])
def agent_tool_approval():
    @task.agent(
        llm_conn_id="pydanticai_default",
        toolsets=[shop],
        output_type=Resolution,
        tool_approval_timeout=timedelta(hours=1),
        on_tool_approval_timeout="deny",
    )
    def handle_ticket():
        return (
            "The customer says orders 7 and 8 never arrived. Look both up, then refund order 7. "
            "Only after you see the result of that refund, refund order 8."
        )

    handle_ticket()


agent_tool_approval()
