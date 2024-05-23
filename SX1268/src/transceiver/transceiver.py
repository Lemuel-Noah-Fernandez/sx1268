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
        c = await loop.run_in_executor(None, sys.stdin.read, 1)
        if c == '\x1b':
            break
        if c == '\x69':
            await loop.run_in_executor(None, transceiver.send_deal)

async def main():
    # Initialize the transceiver object
    transceiver = Transceiver(serial_num="/dev/ttyS0", freq=433, addr=0, power=22, rssi=False, air_speed=2400, relay=False)

    # Set the terminal to non-canonical mode to immediately process input
    tty.setcbreak(sys.stdin.fileno())

    # Clear json files on start up
    DataManager().clear_json_files()

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
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, transceiver.old_settings)
        send_task.cancel()
        await send_task

if __name__ == '__main__':
    asyncio.run(main())
