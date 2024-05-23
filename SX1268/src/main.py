import sys
import select
import termios
import tty
import asyncio
from transceiver import Transceiver
from data_management import DataManager

async def handle_send(transceiver):
    """Handles sending data from user input asynchronously."""
    loop = asyncio.get_event_loop()
    while True:
        try:
            c = await loop.run_in_executor(None, sys.stdin.read, 1)
            if c == '\x1b':
                break
            if c == '\x69':
                await loop.run_in_executor(None, transceiver.send_deal)
        except asyncio.CancelledError:
            break

async def main():
    # Initialize the transceiver object
    transceiver = Transceiver(serial_num="/dev/ttyS0", freq=433, addr=0, power=22, rssi=False, air_speed=2400, relay=False)

    # Set the terminal to non-canonical mode to immediately process input
    tty.setcbreak(sys.stdin.fileno())

    # Clear json files on start up
    DataManager().clear_json_files()

    # Send startup command
    transceiver.startup_command()

    # Start the input coroutine
    send_task = asyncio.create_task(handle_send(transceiver))

    # Listen for commands to receive/send
    try:
        print("Press \033[1;32mEsc\033[0m to exit")
        print("Press \033[1;32mi\033[0m to send")
        while True:
            transceiver.receive_data()
            await asyncio.sleep(0.01)  # Yield control to the event loop

    except KeyboardInterrupt:
        print("\nClosing connection")
        pass
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Send command for program finish
        transceiver.ending_command()
        send_task.cancel()
        try:
            await send_task
        except asyncio.CancelledError:
            pass
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, transceiver.old_settings)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted and closed.")
