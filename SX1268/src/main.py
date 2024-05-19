import sys
import select
import termios
import tty
import threading
from transceiver import Transceiver
from data_management import DataManager

def user_input_thread(transceiver, lock):
    with lock:
        # Temporarily set terminal settings to original for user input
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, transceiver.old_settings)
        print("\nPlease input your commands in the format <component>,<component_id>,<command>: ", end='')
        sys.stdout.flush()
        message = input()
        # Send the message
        transceiver.send_deal(message)
        # Set terminal back to non-canonical mode
        tty.setcbreak(sys.stdin.fileno())

def receive_data_thread(transceiver, lock):
    while True:
        with lock:
            transceiver.receive_data()

def main():
    # Initialize the transceiver object
    transceiver = Transceiver(serial_num="/dev/ttyS0", freq=433, addr=0, power=22, rssi=False, air_speed=2400, relay=False)

    # Set the terminal to non-canonical mode to immediately process input
    tty.setcbreak(sys.stdin.fileno())

    # Clear JSON files on start up
    DataManager().clear_json_files()

    lock = threading.Lock()

    # Start receive data thread
    receive_thread = threading.Thread(target=receive_data_thread, args=(transceiver, lock))
    receive_thread.daemon = True  # Daemonize thread to exit with the program
    receive_thread.start()

    # Listen for commands to receive/send
    try:
        print("Press \033[1;32mEsc\033[0m to exit")
        print("Press \033[1;32mi\033[0m to send")
        while True:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                c = sys.stdin.read(1)
                if c == '\x1b':
                    break
                if c == '\x69':  # 'i' key pressed
                    input_thread = threading.Thread(target=user_input_thread, args=(transceiver, lock))
                    input_thread.start()
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nClosing connection")
        pass
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, transceiver.old_settings)

if __name__ == '__main__':
    main()
