import asyncio
from queue import Queue
import time

from iva import Iva
from iva_communicator import IvaCommunicator


async def main():
    event_queue = Queue()

    iva_communicator = IvaCommunicator('localhost', 5678)
    iva_communicator.start()

    iva = Iva(event_queue, iva_communicator)
    iva.start()

    await asyncio.sleep(3)
    event_queue.put('MORNING')
    await asyncio.sleep(5)
    event_queue.put('MORNING_CALLBACK')
    await asyncio.sleep(5)
    event_queue.put('MORNING_CALLBACK')
    # await iva_communicator.start_morning_routine()

asyncio.run(main())
