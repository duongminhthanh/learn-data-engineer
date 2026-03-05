import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click
import os

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    
    # 1. Tạo chuỗi kết nối và engine
    conn_string = f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    engine = create_engine(conn_string)

    # 2. Cấu hình kiểu dữ liệu (Dtypes) để tối ưu bộ nhớ
    dtype = {
        "VendorID": "Int64", "passenger_count": "Int64", "trip_distance": "float64",
        "RatecodeID": "Int64", "store_and_fwd_flag": "string", "PULocationID": "Int64",
        "DOLocationID": "Int64", "payment_type": "Int64", "fare_amount": "float64",
        "extra": "float64", "mta_tax": "float64", "tip_amount": "float64",
        "tolls_amount": "float64", "improvement_surcharge": "float64",
        "total_amount": "float64", "congestion_surcharge": "float64"
    }
    parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

    # 3. Đường dẫn tải dữ liệu (Có thể tùy biến thêm nếu muốn)
    url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    
    # Sử dụng chunksize để không làm tràn RAM
    df_iter = pd.read_csv(url, chunksize=100000, dtype=dtype, parse_dates=parse_dates)

    # 4. Vòng lặp nạp dữ liệu (Ingestion Loop)
    first = True
    for df_chunk in tqdm(df_iter, desc="Đang nạp dữ liệu"):
        if first:
            # Tạo bảng mới (xóa bảng cũ nếu đã tồn tại)
            df_chunk.head(0).to_sql(name=target_table, con=engine, if_exists="replace")
            first = False
            print(f"Bảng '{target_table}' đã được khởi tạo.")

        # Nạp dữ liệu vào bảng
        df_chunk.to_sql(name=target_table, con=engine, if_exists="append")

    print("Hoàn thành nạp dữ liệu vào Database!")

if __name__ == '__main__':
    run()