import pandas as pd
from sqlalchemy import create_engine
import click



@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')


def run(pg_user, pg_pass, pg_host, pg_port, pg_db):

    url_taxi_Nov_2025 = 'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet'
    url_dataset_with_zones = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'

    target_tables = ['taxi_nov_2015', 'taxi_zones']
                     
    taxi_Nov_2025 = pd.read_parquet(url_taxi_Nov_2025)
    taxi_zone_lookup = pd.read_csv(url_dataset_with_zones)
    dfs = [taxi_Nov_2025, taxi_zone_lookup] 
    
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    for target_table, df in zip(target_tables, dfs):
        # create empty table
        df.head(0).to_sql(
            name=target_table,
            con=engine,
            if_exists="replace"
        )

        #populate table
        df.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )

if __name__ == '__main__':
    run()
