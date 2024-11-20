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
➜  ls -alh --sort=extension mbta-example
Permissions Size User Date Modified Name
.rw-r--r--  320k drew 20 Nov 10:42  gtfs_realtime_data.parquet
.rw-r--r--  117k drew 20 Nov 10:51  Alerts.pb
.rw-r--r--  842k drew 20 Nov 10:52  TripUpdates.pb
.rw-r--r--   72k drew 20 Nov 10:52  VehiclePositions.pb
```