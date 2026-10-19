import sqlite3

from pydantic import BaseModel

from airflow.sdk import dag, task, task_group

MAX_ATTEMPTS = 5

EXPECTED_COLUMNS = ["name", "total_spend"]


class SQLQuery(BaseModel):
    sql: str
    explanation: str


def build_database():
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, full_name TEXT, country_code TEXT);
        CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_ref INTEGER, amount_usd REAL, ordered_at TEXT);
        INSERT INTO customers VALUES (1, 'James T. Kirk', 'US'), (2, 'Jean-Luc Picard', 'FR'), (3, 'Kathryn Janeway', 'US');
        INSERT INTO orders VALUES
            (1, 1, 120.0, '2026-07-03'), (2, 2, 340.5, '2026-08-14'), (3, 3, 99.9, '2026-09-21'),
            (4, 2, 15.0, '2026-09-30'), (5, 1, 410.0, '2026-10-02'), (6, 3, 280.0, '2026-08-01');
        """
    )
    return connection


def query_passes(*, loop):
    return loop.result["passed"]


@dag(
    params={"question": "Which customer spent the most in Q3 2026 (July to September)?"},
    tags=["task_loop"],
)
def agent_text_to_sql():

    @task
    def get_question(params):
        return params["question"]

    @task_group
    def answer_question(question):
        @task
        def gather_feedback(question, *, loop):
            problems = [] if loop.index == 0 else loop.previous["problems"]
            return {"question": question, "problems": problems}

        @task.agent(
            llm_conn_id="pydanticai_default",
            system_prompt=(
                "You write SQLite queries. The database has the tables 'customers' and 'orders'. "
                f"Return exactly these columns, in this order: {', '.join(EXPECTED_COLUMNS)}."
            ),
            output_type=SQLQuery,
        )
        def write_sql(feedback):
            prompt = f"Write a SQL query that answers: {feedback['question']}"
            if feedback["problems"]:
                prompt += "\nYour previous query had these problems, fix them:\n- "
                prompt += "\n- ".join(feedback["problems"])
            return prompt

        @task
        def check_sql(query):
            connection = build_database()
            problems = []
            rows = []
            try:
                cursor = connection.execute(query.sql)
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                if columns != EXPECTED_COLUMNS:
                    problems.append(f"The query returned the columns {columns}, expected {EXPECTED_COLUMNS}.")
                if not rows:
                    problems.append("The query returned no rows.")
            except sqlite3.Error as error:
                schema = [row[0] for row in connection.execute("SELECT sql FROM sqlite_master WHERE type = 'table'")]
                problems.append(f"The database returned an error: {error}. The real schema is: {' '.join(schema)}")
            print(f"SQL: {query.sql}\nRows: {rows}\nProblems: {problems or 'none'}")
            return {"sql": query.sql, "rows": rows, "problems": problems, "passed": not problems}

        check_sql(write_sql(gather_feedback(question)))

    @task
    def report_answer(attempts):
        final = attempts[-1]
        print(f"Answered after {len(attempts)} attempt(s):\n{final['sql']}\n{final['rows']}")

    _get_question = get_question()

    _answer_question = answer_question.partial(question=_get_question).loop(
        max_iterations=MAX_ATTEMPTS, until=query_passes
    )

    _report_answer = report_answer(_answer_question["check_sql"].output)


agent_text_to_sql()
