import serial
import time
import math
from datetime import datetime

EARTH_RADIUS_KM = 6371.0


def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c * 1000  # Return distance in meters


def parse_nmea_sentence(sentence):
    """Parse an NMEA sentence to extract GPS data."""
    if sentence.startswith("$GPGGA"):
        parts = sentence.split(',')
        if len(parts) > 9:
            time_utc = parts[1]
            latitude = convert_to_decimal(parts[2], parts[3])
            longitude = convert_to_decimal(parts[4], parts[5])
            altitude = parts[9]
            return {
                "time_utc": time_utc,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude
            }
    return None


def convert_to_decimal(coord, direction):
    """Convert NMEA latitude/longitude to decimal degrees."""
    if not coord or not direction:
        return None
    degrees = int(coord[:2])
    minutes = float(coord[2:])
    decimal = degrees + (minutes / 60.0)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


def main():
    gps_port = "/dev/ttyUSB0"
    baud_rate = 9600
    log_file = "gps_log.csv"

    # Create log file and write header
    with open(log_file, 'w') as f:
        f.write("Timestamp,Latitude,Longitude,Distance (meters),"
                "Cumulative Distance (meters)\n")

    try:
        # Open the serial port for GPS module communication
        with serial.Serial(gps_port, baud_rate, timeout=1) as serial_port:
            print("Connected to GPS module. Tracking data...")

            prev_lat, prev_lon = None, None
            cumulative_distance = 0.0

            while True:
                # Read a line from the GPS serial data
                data = serial_port.readline().decode('ascii',
                                                     errors='ignore').strip()
                gps_data = parse_nmea_sentence(data)

                if gps_data:
                    lat, lon = gps_data['latitude'], gps_data['longitude']
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Calculate distance if previous position exists
                    if prev_lat is not None and prev_lon is not None:
                        distance = haversine(prev_lat, prev_lon, lat, lon)
                        cumulative_distance += distance
                    else:
                        distance = 0.0

                    # Update previous coordinates
                    prev_lat, prev_lon = lat, lon

                    # Log the data to a CSV file
                    with open(log_file, 'a') as f:
                        f.write(f"{timestamp},{lat},{lon},{distance:.2f},"
                                f"{cumulative_distance:.2f}\n")

                    # Print the information to the console
                    print(f"Timestamp: {timestamp}")
                    print(f"Latitude: {lat}")
                    print(f"Longitude: {lon}")
                    print(f"Distance: {distance:.2f} meters")
                    print(f"Cumulative Distance: {cumulative_distance:.2f}"
                          " meters\n")

                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program...")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
