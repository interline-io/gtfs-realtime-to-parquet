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
pipenv run parquet-tools show gtfs_realtime_data.parquet | code -
```