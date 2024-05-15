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
            "velocity_z": unpacked_data[9],
        }

    def parse_wod_data(self, raw_data):
        """ Parse WOD data from raw bytes to JSON. """
        # Add the specific unpacking format and data structure for WOD data
        return {
            "raw_data": raw_data.hex()
        }

    def parse_commands_data(self, raw_data):
        """ Parse commands data from raw bytes to JSON. """
        # Add the specific unpacking format and data structure for commands data
        return {
            "raw_data": raw_data.hex()
        }

    def parse_misc_data(self, raw_data):
        """ Parse miscellaneous data from raw bytes to JSON. """
        # Add the specific unpacking format and data structure for misc data
        return {
            "raw_data": raw_data.hex()
        }