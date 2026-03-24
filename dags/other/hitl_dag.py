from airflow.sdk import dag, task, Param
from airflow.providers.standard.operators.hitl import HITLOperator 

@dag 
def hitl_dag():

    hitl_task = HITLOperator(
        task_id="review_ticket",
        subject="Customer Ticket #48291 — Feature Request: Dark Mode",
        body=(
            "**Customer:** Love the product — our team uses it every day! One thing that would make "
            "it even better is a dark mode option. Would be great for late-night work sessions.\n\n"
            "**AI Draft Response:** Thank you so much for the kind words and the suggestion! Dark mode "
            "is actually on our roadmap for Q3. I've added your vote to the feature request — we'll "
            "notify you as soon as it's available. Thanks for helping us improve the product!"
        ),
        options=["Approve", "Reject", "Escalate"],
        params={"Additional Information": Param("", type="string")}
    )

hitl_dag()
