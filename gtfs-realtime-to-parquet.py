import pyarrow as pa
import pyarrow.parquet as pq
import requests
import sys
import os
from gtfs_realtime_pb2 import FeedMessage
import tempfile

# Function to download the Protobuf file from a URL and convert it to Parquet
def download_and_convert_pb_to_parquet(url, existing_parquet_path=None):
    # Download the Protobuf data
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download Protobuf file, status code: {response.status_code}")

    # Create a temporary file to store the downloaded data
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name

    # Read the Protobuf data
    with open(temp_file_path, 'rb') as f:
        data = f.read()

    # Parse the Protobuf data
    feed = FeedMessage()
    feed.ParseFromString(data)

    # Extract data into a list of dictionaries
    records = []
    for entity in feed.entity:
        record = {
            'id': entity.id,
            'is_deleted': entity.is_deleted,
        }
        
        if entity.HasField('trip_update'):
            trip_update = entity.trip_update
            record.update({
                'trip_id': trip_update.trip.trip_id,
                'route_id': trip_update.trip.route_id,
                'start_time': trip_update.trip.start_time,
                'start_date': trip_update.trip.start_date,
                'schedule_relationship': trip_update.trip.schedule_relationship,
                'stop_time_updates': [
                    {
                        'stop_sequence': stop_time_update.stop_sequence,
                        'stop_id': stop_time_update.stop_id,
                        'arrival_time': stop_time_update.arrival.time,
                        'arrival_delay': stop_time_update.arrival.delay,
                        'departure_time': stop_time_update.departure.time,
                        'departure_delay': stop_time_update.departure.delay,
                        'schedule_relationship': stop_time_update.schedule_relationship
                    }
                    for stop_time_update in trip_update.stop_time_update
                ]
            })
        
        if entity.HasField('vehicle'):
            vehicle = entity.vehicle
            record.update({
                'vehicle_id': vehicle.vehicle.id,
                'vehicle_label': vehicle.vehicle.label,
                'license_plate': vehicle.vehicle.license_plate,
                'position_latitude': vehicle.position.latitude,
                'position_longitude': vehicle.position.longitude,
                'bearing': vehicle.position.bearing,
                'odometer': vehicle.position.odometer,
                'speed': vehicle.position.speed,
                'current_stop_sequence': vehicle.current_stop_sequence,
                'current_status': vehicle.current_status,
                'timestamp': vehicle.timestamp,
                'congestion_level': vehicle.congestion_level,
                'occupancy_status': vehicle.occupancy_status
            })
        
        if entity.HasField('alert'):
            alert = entity.alert
            record.update({
                'active_period': [
                    {
                        'start': period.start,
                        'end': period.end
                    }
                    for period in alert.active_period
                ],
                'informed_entity': [
                    {
                        'agency_id': entity.agency_id,
                        'route_id': entity.route_id,
                        'route_type': entity.route_type,
                        'stop_id': entity.stop_id,
                        'trip_id': entity.trip.trip_id
                    }
                    for entity in alert.informed_entity
                ],
                'cause': alert.cause,
                'effect': alert.effect,
                'url': alert.url.translation[0].text if alert.url.translation else None,
                'header_text': alert.header_text.translation[0].text if alert.header_text.translation else None,
                'description_text': alert.description_text.translation[0].text if alert.description_text.translation else None
            })
        
        records.append(record)

    # Define PyArrow schema
    schema = pa.schema([
        ('id', pa.string()),
        ('is_deleted', pa.bool_()),
        ('trip_id', pa.string()),
        ('route_id', pa.string()),
        ('start_time', pa.string()),
        ('start_date', pa.string()),
        ('schedule_relationship', pa.int32()),
        ('stop_time_updates', pa.list_(pa.struct([
            ('stop_sequence', pa.int32()),
            ('stop_id', pa.string()),
            ('arrival_time', pa.int64()),
            ('arrival_delay', pa.int32()),
            ('departure_time', pa.int64()),
            ('departure_delay', pa.int32()),
            ('schedule_relationship', pa.int32())
        ]))),
        ('vehicle_id', pa.string()),
        ('vehicle_label', pa.string()),
        ('license_plate', pa.string()),
        ('position_latitude', pa.float64()),
        ('position_longitude', pa.float64()),
        ('bearing', pa.float64()),
        ('odometer', pa.float64()),
        ('speed', pa.float64()),
        ('current_stop_sequence', pa.int32()),
        ('current_status', pa.int32()),
        ('timestamp', pa.int64()),
        ('congestion_level', pa.int32()),
        ('occupancy_status', pa.int32()),
        ('active_period', pa.list_(pa.struct([
            ('start', pa.int64()),
            ('end', pa.int64())
        ]))),
        ('informed_entity', pa.list_(pa.struct([
            ('agency_id', pa.string()),
            ('route_id', pa.string()),
            ('route_type', pa.int32()),
            ('stop_id', pa.string()),
            ('trip_id', pa.string())
        ]))),
        ('cause', pa.int32()),
        ('effect', pa.int32()),
        ('url', pa.string()),
        ('header_text', pa.string()),
        ('description_text', pa.string())
    ])

    # Convert records to PyArrow Table
    table = pa.Table.from_pydict({
        'id': [record.get('id') for record in records],
        'is_deleted': [record.get('is_deleted') for record in records],
        'trip_id': [record.get('trip_id') for record in records],
        'route_id': [record.get('route_id') for record in records],
        'start_time': [record.get('start_time') for record in records],
        'start_date': [record.get('start_date') for record in records],
        'schedule_relationship': [record.get('schedule_relationship') for record in records],
        'stop_time_updates': [record.get('stop_time_updates') for record in records],
        'vehicle_id': [record.get('vehicle_id') for record in records],
        'vehicle_label': [record.get('vehicle_label') for record in records],
        'license_plate': [record.get('license_plate') for record in records],
        'position_latitude': [record.get('position_latitude') for record in records],
        'position_longitude': [record.get('position_longitude') for record in records],
        'bearing': [record.get('bearing') for record in records],
        'odometer': [record.get('odometer') for record in records],
        'speed': [record.get('speed') for record in records],
        'current_stop_sequence': [record.get('current_stop_sequence') for record in records],
        'current_status': [record.get('current_status') for record in records],
        'timestamp': [record.get('timestamp') for record in records],
        'congestion_level': [record.get('congestion_level') for record in records],
        'occupancy_status': [record.get('occupancy_status') for record in records],
        'active_period': [record.get('active_period') for record in records],
        'informed_entity': [record.get('informed_entity') for record in records],
        'cause': [record.get('cause') for record in records],
        'effect': [record.get('effect') for record in records],
        'url': [record.get('url') for record in records],
        'header_text': [record.get('header_text') for record in records],
        'description_text': [record.get('description_text') for record in records]
    }, schema=schema)

    # Write or append to Parquet
    if existing_parquet_path and os.path.exists(existing_parquet_path):
        # Read existing Parquet file
        existing_table = pq.read_table(existing_parquet_path)
        # Concatenate the new table with the existing one
        combined_table = pa.concat_tables([existing_table, table])
        # Write back to the Parquet file
        pq.write_table(combined_table, existing_parquet_path)
    else:
        # Write to a new Parquet file
        pq.write_table(table, 'gtfs_realtime_data.parquet')

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script.py <URL> [existing_parquet_path]")
        sys.exit(1)

    url = sys.argv[1]
    existing_parquet_path = sys.argv[2] if len(sys.argv) == 3 else None
    download_and_convert_pb_to_parquet(url, existing_parquet_path)
