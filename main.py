from iva_communicator import IvaCommunicator


def main():
    iva_communicator = IvaCommunicator('localhost', 5678)
    iva_communicator.start()


main()
