To generate proto bindings:

```sh
wget https://raw.githubusercontent.com/google/transit/refs/heads/master/gtfs-realtime/proto/gtfs-realtime.proto

protoc --python_out=. gtfs-realtime.proto
```

To run:

```sh
pipenv run python gtfs-realtime-to-parquet.py https://cdn.mbta.com/realtime/VehiclePositions.pb
pipenv run python gtfs-realtime-to-parquet.py https://cdn.mbta.com/realtime/TripUpdates.pb gtfs_realtime_data.parquet
pipenv run python gtfs-realtime-to-parquet.py https://cdn.mbta.com/realtime/Alerts.pb gtfs_realtime_data.parquet
```

To view output:

```sh
pipenv run parquet-tools show mbta-example/gtfs_realtime_data.parquet | code -
```

or using DuckDB:

```sh
pipenv run duckdb -c "COPY (SELECT * FROM 'mbta-example/gtfs_realtime_data.parquet') TO stdout (FORMAT 'csv', HEADER TRUE);" | code -
```

Comparing size on disk:

```sh
➜  du -ch mbta-example/*.pb
116K    mbta-example/Alerts.pb
824K    mbta-example/TripUpdates.pb
 72K    mbta-example/VehiclePositions.pb
1.0M    total

tar -czvf mbta-example-pbs.tar.gz *.pb
du -h mbta-example/*.gz
356K	mbta-example/mbta-example-pbs.tar.gz

➜  du -h mbta-example/*.geoparquet 
 36K    mbta-example/gtfs_realtime_data.geoparquet
```