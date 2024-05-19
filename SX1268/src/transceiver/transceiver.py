import json
import sys
import termios
from .sx126x import SX126x
import tty
from AX25UI import AX25UIFrameDecoder, AX25UIFrame
from data_management import DataManager

class Transceiver(SX126x):
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

        # Data manajer initialisation
        self.data_manager = DataManager()

        # File path of received commands for visualization
        self.json_file_path = 'received_commands.json'
    
    def send_deal(self) -> None:
        """Sends data after taking input from the user"""
        # Temporarily set terminal settings to original for user input
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        print("\nPlease input your commands in the format <component>,<component_id>,<command>: ", end='')
        message = input()

        # Frame encoder
        ssid_type = 0b0111  # Command data type
        ax25_frame = AX25UIFrame(message, ssid_type)
        frame = ax25_frame.create_frame()

        # Package encoder details
        DEFAULT_ADDRESS = 0
        offset_frequency = self.freq - (850 if self.freq > 850 else 410)        
        data = (bytes([DEFAULT_ADDRESS >> 8]) + 
                bytes([DEFAULT_ADDRESS & 0xff]) +
                bytes([offset_frequency]) + 
                bytes([self.addr >> 8]) + 
                bytes([self.addr & 0xff]) + 
                bytes([self.offset_freq]) + 
                frame)
        self.send(data)
        print("Message sent!")

        # Reset terminal to non-canonical mode
        tty.setcbreak(sys.stdin.fileno())
        return None


    def receive_data(self):
        data = self.receive()

        if data:
            try:
                # Make sure data is in byts
                if isinstance(data, bytes):
                    # Initialise decoder
                    decoder = AX25UIFrameDecoder()
                    decoded_frame = decoder.decode_ax25_frame(data)

                    # Take out ssid and info
                    ssid = decoded_frame["d_ssid"]
                    info_data = decoded_frame["info"]

                    # Append to json files
                    json_data = self.data_manager.convert_bytes_to_json(info_data, ssid)
                    self.data_manager.append_to_json(json_data, ssid)
                    return decoded_frame
                else:
                    print("Received non-byte data")
                    return None
            except Exception as e:
                print(f"Error handling received data: {str(e)}")
                return None

    def reset_terminal_settings(self):
        """ Reset terminal settings to their original state. """
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        return None

    