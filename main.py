import asyncio
import time

from iva_communicator import IvaCommunicator


async def main():
    iva_communicator = IvaCommunicator('localhost', 5678)
    iva_communicator.start()


asyncio.run(main())
