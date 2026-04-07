from airflow.sdk import dag, task


async def fetch_one():
    import httpx

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get("https://httpbin.org/delay/5")
        return response.json()


@dag
def async_task_decorator_example_many():

    @task
    async def fetch_concurrently():
        import asyncio
        import time

        start = time.monotonic()
        results = await asyncio.gather(*[fetch_one() for _ in range(20)])
        elapsed = time.monotonic() - start
        print(f"All 20 done in {elapsed:.1f}s")

    fetch_concurrently()


async_task_decorator_example_many()
