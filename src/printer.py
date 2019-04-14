import cups

class Printer():
    def __init__(self, printer, conn):
        self.name = printer
        self._conn = conn
        self._count = 0

    def print_file(self, file_name):
        job = self._conn.printFile(
            self.name,
            file_name,
            "{}_{}".format(self._count, file_name),
            {
                'StpColorPrecision': 'Best',
                'ColorModel': 'RBG',
                'StpBorderless': 'True',
                'StpImageType': 'Photo',
                'StpiShrinkOutput': 'Expand',
                'StpSaturation': '1400',
                'StpContrast': '1500',
                'StpCyanBalance': '800',
            },
        )
        self._count += 1
        return job


def get_printer():
    conn = cups.Connection()
    printers = conn.getPrinters()
    if len(printers) == 0:
        return None
    return Printer(next(iter(printers)), conn)
