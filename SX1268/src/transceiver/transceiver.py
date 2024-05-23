import sys
import select
import termios
import tty
import threading
from transceiver import Transceiver
from data_management import DataManager

def handle_send(transceiver):
    """Handles sending data from user input in a separate thread."""
    while True:
        c = sys.stdin.read(1)
        if c == '\x1b': 
            break
        if c == '\x69':
            transceiver.send_deal()

def main():
    # Initialize the transceiver object
    transceiver = Transceiver(serial_num="/dev/ttyS0", freq=433, addr=0, power=22, rssi=False, air_speed=2400, relay=False)

    # Set the terminal to non-canonical mode to immediately process input
    tty.setcbreak(sys.stdin.fileno())

    # Clear json files on start up
    DataManager().clear_json_files()

    # Start the input thread
    input_thread = threading.Thread(target=handle_send, args=(transceiver,))
    input_thread.daemon = True
    input_thread.start()

    # Listen for commands to receive/send
    try:
        print("Press \033[1;32mEsc\033[0m to exit")
        print("Press \033[1;32mi\033[0m to send")
        while True:
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
