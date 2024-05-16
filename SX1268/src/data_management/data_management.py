import json
import struct

class DataManager:
    def __init__(self):
        self.json_files = {
            0b1110: 'wod_data.json',       # Whole Orbit Data
            0b1101: 'pose_data.json',      # Satellite Pose
            0b1011: 'misc_data.json',      # Miscellaneous Data
            0b0111: 'commands_data.json',  # Commands
            0b1111: 'science_data.json'    # Science Data
        }

        # WOD data information
        self.satellite_id = None
        self.time_field = None
        self.datasets = []

    @staticmethod
    def decode_voltage(voltage):
        return (voltage + 60) / 20.0

    @staticmethod
    def decode_current(current):
        return (current - 127) / 127.0

    @staticmethod
    def decode_bus_current(current):
        return current / 40.0

    @staticmethod
    def decode_temperature(temp):
        return (temp - 60) / 4.0

    def append_to_json(self, data, ssid):
        """ Append data to a JSON file based on SSID"""
        file_path = self.json_files.get(ssid)
        try:
            with open(file_path, 'r+') as file:
                existing_data = json.load(file)
                existing_data.append(data)
                file.seek(0)
                json.dump(existing_data, file, indent=4)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(file_path, 'w') as file:
                json.dump([data], file, indent=4)

    def clear_json_files(self):
        """ Clears all json files on startup"""
        for path in self.json_files.values():
            try:
                with open(path, 'w') as file:
                    file.write('[]')
            except Exception as e:
                print(f"Failed to clear JSON file {path}: {str(e)}")

    def convert_bytes_to_json(self, raw_data, ssid):
        """ Convert raw byte data to JSON format based on SSID. """
        if ssid == 0b1111:  # Science Data
            return self.parse_science_data(raw_data)
        elif ssid == 0b1110:  # Whole Orbit Data
            return self.parse_wod_data(raw_data)
        elif ssid == 0b1101:  # Satellite Pose
            return self.parse_satellite_pose(raw_data)
        elif ssid == 0b1011:  # Miscellaneous Data
            return self.parse_misc_data(raw_data)
        elif ssid == 0b0111:  # Commands
            return self.parse_commands_data(raw_data)
        else:
            return {"raw_data": raw_data.hex()}

    def parse_science_data(self, raw_data):
        """ Parse science data from raw bytes to JSON. """
        format_string = '<fff fff f i i'
        unpacked_data = struct.unpack(format_string, raw_data)
        return {
            "debris_position_x": unpacked_data[0],
            "debris_position_y": unpacked_data[1],
            "debris_position_z": unpacked_data[2],
            "debris_velocity_x": unpacked_data[3],
            "debris_velocity_y": unpacked_data[4],
            "debris_velocity_z": unpacked_data[5],
            "debris_diameter": unpacked_data[6],
            "time_of_detection": unpacked_data[7],
            "object_count": unpacked_data[8],
        }

    def parse_satellite_pose(self, raw_data):
        """ Parse satellite pose data from raw bytes to JSON. """
        format_string = '<fff ffff fff'
        unpacked_data = struct.unpack(format_string, raw_data)
        return {
            "position_x": unpacked_data[0],
            "position_y": unpacked_data[1],
            "position_z": unpacked_data[2],
            "orientation_x": unpacked_data[3],
            "orientation_y": unpacked_data[4],
            "orientation_z": unpacked_data[5],
            "orientation_w": unpacked_data[6],
            "velocity_x": unpacked_data[7],
            "velocity_y": unpacked_data[8],
            "velocity_z": unpacked_data[9]
        }

    def parse_misc_data(self, raw_data):
        """ Parse miscellaneous data from raw bytes to JSON. """
        return {
            "raw_data": raw_data.hex()
        }

    def parse_wod_data(self, raw_data):
        """Parse WOD data from raw bytes to JSON."""
        # Unpack the packet identifier (1 byte)
        packet_id = raw_data[0]
        dataset_size = struct.calcsize('8B')

        if packet_id == 1:
            # This is the first packet, so we need to parse the satellite ID and time field
            satellite_id_format = '5s'
            satellite_id_size = struct.calcsize(satellite_id_format)
            self.satellite_id = struct.unpack(satellite_id_format, raw_data[1:1 + satellite_id_size])[0].decode('ascii')

            time_format = '<I'
            time_size = struct.calcsize(time_format)
            self.time_field = struct.unpack(time_format, raw_data[1 + satellite_id_size:1 + satellite_id_size + time_size])[0]

            dataset_data = raw_data[1 + satellite_id_size + time_size:]
            num_datasets = 16  # First packet contains 16 datasets

        elif packet_id == 2:
            # This is the second packet, so we only need to parse the datasets
            dataset_data = raw_data[1:]
            num_datasets = 16  # Second packet contains 16 datasets

        else:
            raise ValueError(f"Unknown packet_id: {packet_id}")

        for i in range(num_datasets):
            if len(dataset_data) < (i + 1) * dataset_size:
                break
            dataset_chunk = dataset_data[i * dataset_size:(i + 1) * dataset_size]
            unpacked_dataset = struct.unpack('8B', dataset_chunk)
            self.datasets.append({
                "satellite_mode": unpacked_dataset[0],
                "battery_voltage": self.decode_voltage(unpacked_dataset[1]),
                "battery_current": self.decode_current(unpacked_dataset[2]),
                "regulated_bus_current_3v3": self.decode_bus_current(unpacked_dataset[3]),
                "regulated_bus_current_5v": self.decode_bus_current(unpacked_dataset[4]),
                "temperature_comm": self.decode_temperature(unpacked_dataset[5]),
                "temperature_eps": self.decode_temperature(unpacked_dataset[6]),
                "temperature_battery": self.decode_temperature(unpacked_dataset[7])
            })

        if packet_id == 2:
            parsed_data = {
                "satellite_id": self.satellite_id,
                "time_field": self.time_field,
                "datasets": self.datasets
            }
            # Clear the stored data for the next complete set of packets
            self.satellite_id = None
            self.time_field = None
            self.datasets = []
            return parsed_data
        return None  # Return None if only the first packet is processed so far
