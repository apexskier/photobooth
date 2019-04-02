import cups

class Printer():
    def __init__(self, printer, conn):
        self._printer = printer
        self._conn = conn
        self._count = 0


    def print_file(self, file_name):
        self._conn.printFile(
            self._printer,
            file_name,
            "{}_{}".format(self._count, file_name),
            {
                'StpColorPrecision': 'Best',
                'ColorModel': 'RBG',
                'StpBorderless': 'True',
                'StpImageType': 'Photo',
                'StpiShrinkOutput': 'Expand',
            },
        )
        self._count += 1


def get_printer():
    conn = cups.Connection()
    printers = conn.getPrinters()
    if len(printers) == 0:
        return None
    return Printer(next(iter(printers)), conn)
