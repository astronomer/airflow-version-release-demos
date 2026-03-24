from airflow.sdk import dag, task


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


@dag
def async_task_decorator_example():

    @task
    async def fetch_concurrently():
        import asyncio
        import time

        start = time.monotonic()
        slow, fast = await asyncio.gather(fetch_one(), fetch_two())
        elapsed = time.monotonic() - start
        print(f"Both done in {elapsed:.1f}s")

    fetch_concurrently()


async_task_decorator_example()
