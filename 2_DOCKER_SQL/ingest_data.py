import os
import pandas as pd
from sqlalchemy import create_engine
import argparse
import time
import pyarrow.parquet as pq



def main(params):

    user = params.user
    password = params.password
    host = params.host
    port = params.port
    database = params.database
    table = params.table
    parquet_url = params.parquet_url
    parquet_name = 'data.parquet'

    #download parquet file
    os.system(f'wget {parquet_url} -O {parquet_name}')

    os.system('wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv -O taxi+_zone_lookup.csv')


    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    engine.connect()

    #import zone data
    df_zones = pd.read_csv('taxi+_zone_lookup.csv')
    df_zones.to_sql(name='zones', con=engine, if_exists='replace')


    print("DATA INGESTION INTO POSTGRESQL")
    start_time = time.time()

    parquet_file = pq.ParquetFile(parquet_name)
    
    for batch in parquet_file.iter_batches():
        
        print("RecordBatch")
        batch_df = batch.to_pandas()
        batch_df.to_sql(name=table, con=engine, if_exists='append',index=False)
        
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest Parquet data to PostgreSQL')

    # user
    # password
    # host
    # port
    # database name
    # table name
    # URL of Parquet 

    parser.add_argument('--user',help='User name for PostgreSQL')
    parser.add_argument('--password',help='Password for PostgreSQL')
    parser.add_argument('--host',help='Host for PostgreSQL')
    parser.add_argument('--port',help='Port for PostgreSQL')
    parser.add_argument('--database',help='Database name for PostgreSQL')
    parser.add_argument('--table',help='Table name for PostgreSQL')
    parser.add_argument('--parquet_url',help='URL of parquet file')



    args = parser.parse_args()


    main(args)





