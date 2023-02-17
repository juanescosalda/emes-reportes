
import logging
from server.report import EmesReport

logging.basicConfig(
    filename='reportes.log',
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)


def main():
    # Init server-side
    emes = EmesReport()

    # Init client-side
    from client.ui import run_ui
    run_ui(emes)


if __name__ == '__main__':
    main()
