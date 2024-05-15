import json
import sys
import termios
import sx126x
from sx126x import sx126x
import struct
from AX25UI import AX25UIFrameDecoder, AX25UIFrame

class Transceiver(sx126x):
    def __init__(
            self, 
            serial_num="/dev/ttyS0", 
            freq=433, 
            addr=0, 
            power=22, 
            rssi=False, 
            air_speed=2400, 
            relay=False
        ) -> None:
        super().__init__(serial_num=serial_num, freq=freq, addr=addr, power=power, rssi=rssi, air_speed=air_speed, relay=relay)
        
        # Terminal settings
        self.old_settings = termios.tcgetattr(sys.stdin)

        # File path of received commands for visualization
        self.json_file_path = 'received_commands.json'
    
    def send_deal(
            self, 
            message: str
        ) -> None:
        """Sends a message after encoding

        Args:
            message (str): _description_

        Returns:
            _type_: _description_
        """
        print("\nPlease input your commands in the format <component>,<component_id>,<command>: ", end='')
        message = input()
        DEFAULT_ADDRESS = 0
        offset_frequency = self.freq - (850 if self.freq > 850 else 410)
        data = (bytes([DEFAULT_ADDRESS >> 8]) + 
                bytes([DEFAULT_ADDRESS & 0xff]) +
                bytes([offset_frequency]) + 
                bytes([self.addr >> 8]) + 
                bytes([self.addr & 0xff]) + 
                bytes([self.offset_freq]) + 
                message)
        self.send(data)
        print("Message sent!")
        return None


    # def receive_data(self):
    #     data = self.receive()

    #     # When receiving a new command
    #     if data:
    #         try:
    #             # Split data to determine message type
    #             if isinstance(data, bytes):
    #                 data = data.decode('utf-8')
    #             message = data.split(",")

    #             # For uplink commands
    #             if len(message) == 3:
    #                 component, component_id, command = message
    #                 uplink_command = command_msg()
    #                 uplink_command.component = component
    #                 uplink_command.component_id = int(component_id)
    #                 uplink_command.command = command
    #                 return uplink_command

    #             else:
    #                 return None
            
    #         except Exception as e:
    #             print(f"Error handling received data: {str(e)}")


    def receive_data(self):
        data = self.receive()

        if data:
            try:
                if isinstance(data, bytes):
                    decoder = AX25UIFrameDecoder()
                    decoded_frame = decoder.decode_ax25_frame(data)
                    return decoded_frame
                else:
                    print("Received non-byte data")
                    return None
            except Exception as e:
                print(f"Error handling received data: {str(e)}")
                return None

    # def decode_ax25UI_frame(self, frame):
    #     """Decode an AX.25 frame and extract the source, destination, SSID, and info fields."""
    #     if frame[0] != 0x7E or frame[-1] != 0x7E:
    #         raise ValueError("Invalid AX.25 frame")

    #     # Decode destination address
    #     destination_callsign = ''.join([chr((frame[i] >> 1) & 0x7F) for i in range(1, 7)]).strip()
    #     destination_ssid = (frame[7] >> 1) & 0x0F

    #     # Decode source address
    #     source_callsign = ''.join([chr((frame[i] >> 1) & 0x7F) for i in range(8, 14)]).strip()
    #     source_ssid = (frame[14] >> 1) & 0x0F

    #     # Control field
    #     control_field = frame[15]

    #     # PID field
    #     pid_field = frame[16]

    #     # Information field
    #     info_field = frame[17:-3].decode('ascii')

    #     # FCS field
    #     received_fcs = frame[-3:-1]
    #     calculated_fcs = self.compute_fcs(frame[1:-3])

    #     if received_fcs != calculated_fcs:
    #         raise ValueError("FCS check failed")

    #     return {
    #         'destination_callsign': destination_callsign,
    #         'destination_ssid': destination_ssid,
    #         'source_callsign': source_callsign,
    #         'source_ssid': source_ssid,
    #         'control_field': control_field,
    #         'pid_field': pid_field,
    #         'info_field': info_field
    #     }
    

    # def compute_fcs(self, frame):
    #     """Compute the Frame Check Sequence (FCS) for a given frame using the CRC-CCITT algorithm."""
    #     fcs = 0xFFFF
    #     for byte in frame:
    #         fcs ^= byte
    #         for _ in range(8):
    #             if fcs & 0x01:
    #                 fcs = (fcs >> 1) ^ 0x840  # Polynomial for CRC-CCITT
    #             else:
    #                 fcs >>= 1
    #     fcs = ~fcs & 0xFFFF
    #     return struct.pack('<H', fcs)

    def reset_terminal_settings(self):
        """ Reset terminal settings to their original state. """
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        return None

    