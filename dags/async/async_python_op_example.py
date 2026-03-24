from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import dag


async def fetch_one():
    import httpx

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get("https://httpbin.org/delay/5")
        return response.json()


async def fetch_two():
    import httpx

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get("https://httpbin.org/delay/5")
        return response.json()


async def fetch_concurrently():
    import asyncio
    import time

    start = time.monotonic()
    await asyncio.gather(fetch_one(), fetch_two())
    elapsed = time.monotonic() - start
    print(f"Both done in {elapsed:.1f}s")


@dag
def async_python_op_example():
    PythonOperator(
        task_id="fetch_concurrently",
        python_callable=fetch_concurrently,
    )


async_python_op_example()
