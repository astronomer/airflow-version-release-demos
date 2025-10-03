"""
## Human-in-the-Loop (HITL) Example DAG

This DAG demonstrates various human-in-the-loop patterns using Airflow's built-in HITL operators:
- Manual approval/rejection tasks
- Option selection with single or multiple choices
- Human input collection with custom parameters
- Conditional branching based on human decisions

The DAG simulates a data processing workflow that requires human oversight at key stages,
such as data quality approval, processing method selection, and final validation.

For more information on HITL operators, see:
https://www.astronomer.io/docs/learn/airflow-human-in-the-loop
"""

from airflow.sdk import dag, task
from airflow.providers.standard.operators.hitl import (
    ApprovalOperator,
    HITLOperator,
    HITLBranchOperator,
    HITLEntryOperator,
)
from airflow.providers.standard.operators.bash import BashOperator
from pendulum import datetime, duration


# -------------- #
# DAG Definition #
# -------------- #


@dag(
    start_date=datetime(2025, 1, 15),
    schedule=None,  # Manual trigger only for this example
    max_consecutive_failed_dag_runs=3,
    doc_md=__doc__,
    default_args={
        "owner": "Data Team",
        "retries": 1,
        "retry_delay": duration(minutes=5),
    },
    tags=["example", "hitl", "approval", "human-in-the-loop"],
    is_paused_upon_creation=False,
    catchup=False,
)
def human_in_the_loop_workflow():
    """
    A comprehensive example of human-in-the-loop workflows in Airflow.
    """

    # ---------------- #
    # Task Definitions #
    # ---------------- #

    @task
    def simulate_data_processing():
        """
        Simulate initial data processing that generates results requiring human review.
        """
        import random

        # Simulate some data processing metrics
        metrics = {
            "records_processed": random.randint(1000, 5000),
            "data_quality_score": round(random.uniform(0.85, 0.99), 3),
            "processing_time_minutes": random.randint(10, 60),
            "anomalies_detected": random.randint(0, 15),
        }

        print(f"Data processing completed with metrics: {metrics}")
        return metrics

    # 1. Approval Task - Simple approve/reject decision
    data_quality_approval = ApprovalOperator(
        task_id="data_quality_approval",
        subject="Data Quality Review Required",
        body="""
## Data Processing Results

Please review the data processing results from the previous task.

**Key Metrics:**
- Records processed: {{ ti.xcom_pull(task_ids='simulate_data_processing')['records_processed'] }}
- Data quality score: {{ ti.xcom_pull(task_ids='simulate_data_processing')['data_quality_score'] }}
- Anomalies detected: {{ ti.xcom_pull(task_ids='simulate_data_processing')['anomalies_detected'] }}

**Action Required:**
- ✅ **Approve** if data quality score > 0.90 and anomalies < 10
- ❌ **Reject** if data quality requires investigation

Select your decision below:
        """,
        defaults=["Approve"],  # Default to approval if timeout
    )

    # 2. Option Selection Task - Choose processing method
    processing_method_selection = HITLOperator(
        task_id="select_processing_method",
        subject="Choose Data Processing Method",
        body="""
## Processing Method Selection

Based on the data quality review, please select the appropriate processing method:

**Available Options:**
- **Standard Processing**: For high-quality data (recommended for quality score > 0.95)
- **Enhanced Validation**: Additional checks for medium-quality data (quality score 0.90-0.95)
- **Deep Cleaning**: Comprehensive data cleaning for lower-quality data (quality score < 0.90)

Choose the most appropriate method based on the data quality metrics.
        """,
        options=["Standard Processing", "Enhanced Validation", "Deep Cleaning"],
        defaults=["Enhanced Validation"],  # Default option
    )

    # 3. Input Collection Task - Gather custom parameters
    custom_parameters_input = HITLEntryOperator(
        task_id="collect_custom_parameters",
        subject="Configure Processing Parameters",
        body="""
## Custom Processing Parameters

Please provide custom parameters for the selected processing method:
        """,
        params={
            "batch_size": {
                "type": "integer",
                "minimum": 100,
                "maximum": 10000,
                "default": 1000,
                "description": "Number of records to process in each batch",
            },
            "validation_threshold": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.95,
                "description": "Minimum quality threshold for validation",
            },
            "enable_monitoring": {
                "type": "boolean",
                "default": True,
                "description": "Enable real-time monitoring during processing",
            },
            "notification_email": {
                "type": "string",
                "format": "email",
                "description": "Email address for processing notifications (optional)",
            },
        },
    )

    # 4. Branch Selection Task - Choose execution path
    execution_path_selection = HITLBranchOperator(
        task_id="choose_execution_path",
        subject="Select Execution Path",
        body="""
## Execution Path Selection

Based on the processing configuration, choose how to proceed:

**Available Paths:**
- **immediate_execution**: Start processing immediately
- **scheduled_execution**: Schedule processing for later
- **manual_review**: Require additional manual review before processing
        """,
        options=["immediate_execution", "scheduled_execution", "manual_review"],
    )

    # Downstream tasks for different execution paths
    immediate_execution = BashOperator(
        task_id="immediate_execution",
        bash_command="""
        echo "Starting immediate data processing..."
        echo "Batch size: {{ ti.xcom_pull(task_ids='collect_custom_parameters')['params_input']['batch_size'] }}"
        echo "Validation threshold: {{ ti.xcom_pull(task_ids='collect_custom_parameters')['params_input']['validation_threshold'] }}"
        echo "Monitoring enabled: {{ ti.xcom_pull(task_ids='collect_custom_parameters')['params_input']['enable_monitoring'] }}"
        sleep 5
        echo "Immediate processing completed successfully!"
        """,
    )

    scheduled_execution = BashOperator(
        task_id="scheduled_execution",
        bash_command="""
        echo "Scheduling data processing for later execution..."
        echo "Processing job queued with custom parameters"
        echo "Notification will be sent when processing begins"
        """,
    )

    manual_review = HITLOperator(
        task_id="manual_review",
        subject="Additional Manual Review",
        body="""
## Additional Review Required

The processing parameters require additional manual review before execution.

**Review Items:**
- Confirm processing method selection
- Validate custom parameters
- Ensure notification settings are correct

Please select your final decision:
        """,
        options=["Proceed with Processing", "Modify Parameters", "Cancel Processing"],
        defaults=["Proceed with Processing"],
    )

    @task
    def final_status_report():
        """
        Generate a final status report based on all human decisions made.
        """
        # This task will compile all the human decisions and generate a summary
        print("=== Human-in-the-Loop Workflow Summary ===")
        print("All human decision points have been completed.")
        print("Processing workflow ready for execution.")
        return "Workflow completed successfully"

    # ------------------------------------ #
    # Task Dependencies                    #
    # ------------------------------------ #

    # Main workflow path
    data_metrics = simulate_data_processing()

    # Human approval chain
    (
        data_metrics
        >> data_quality_approval
        >> processing_method_selection
        >> custom_parameters_input
    )

    # Branch based on execution path choice
    custom_parameters_input >> execution_path_selection

    # Different execution paths
    execution_path_selection >> [
        immediate_execution,
        scheduled_execution,
        manual_review,
    ]

    # Final status (manual_review can lead here, others end their paths)
    manual_review >> final_status_report()
    immediate_execution >> final_status_report()
    scheduled_execution >> final_status_report()


# Instantiate the DAG
human_in_the_loop_workflow()
