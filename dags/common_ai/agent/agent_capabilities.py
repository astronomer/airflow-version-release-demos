"""
## Agent capabilities

`capabilities=` on `@task.agent` takes pydantic-ai capabilities, which hook into
the agent run. `Thinking(effort="high")` asks the model to reason before it
answers; for OpenAI reasoning models such as `gpt-5-mini` it's sent as the
reasoning effort. New in Common AI 1.0.
"""

from pydantic_ai.capabilities import Thinking

from airflow.sdk import dag, task


@dag(tags=["common_ai"])
def agent_capabilities():
    @task.agent(
        llm_conn_id="pydanticai_default",
        system_prompt="You are a careful flight planner. Answer in two sentences.",
        capabilities=[Thinking(effort="high")],
    )
    def plan_fuel_stop():
        return (
            "A ship burns 2.5 tonnes of fuel per day and carries 30 tonnes. "
            "The trip from Earth to Ceres takes 14 days. Does it need a fuel stop, "
            "and if so, after how many days at the latest?"
        )

    plan_fuel_stop()


agent_capabilities()
