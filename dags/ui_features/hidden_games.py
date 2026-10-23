from airflow.sdk import Asset, chain, dag, task


@dag(tags=["scoped_plugin_example"])
def hidden_games():

    @task
    def minesweeper():
        pass

    @task
    def slitherlink():
        pass

    @task(outlets=[Asset("the_high_seas")])
    def battleships():
        pass

    chain(minesweeper(), slitherlink(), battleships())


hidden_games()
