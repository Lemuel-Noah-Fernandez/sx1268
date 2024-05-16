import sys
import select
import termios
import tty
from threading import Timer
import json
from transceiver import Transceiver

def main():
    # Initialize the transceiver object
    transceiver = Transceiver(serial_num="/dev/ttyS0", freq=433, addr=0, power=22, rssi=False, air_speed=2400, relay=False)

    # Set the terminal to non-canonical mode to immediately process input
    # old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    # Clear json file
    # clear_json_file(json_file_path)

    # Listen for commands to receive/send
    try:
        print("Press \033[1;32mEsc\033[0m to exit")
        print("Press \033[1;32mi\033[0m to send")
        while True:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                c = sys.stdin.read(1)
                if c == '\x1b': break
                if c == '\x69':
                    transceiver.send_deal()
                sys.stdout.flush()
            
            # Received commands
            transceiver.receive_data()

    except KeyboardInterrupt:
        print("\nClosing connection")
        pass
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, transceiver.old_settings)

if __name__ == '__main__':
    main()