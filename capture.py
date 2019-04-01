"""
Photobooth capture script
"""

import logging
import os
import datetime
import time
import sys

from PIL import Image, ImageOps
import rawpy

from camera import Camera
from templates import TEMPLATE_SQUARE, TEMPLATE_STRIPS
from cli_input import wait_for_input
from printer import get_printer

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

COUNTDOWN = 3

def countdown():
    """Display a countdown timer"""
    for i in reversed(range(0, COUNTDOWN)):
        print(i + 1)
        time.sleep(1)

def read_file(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension == ".jpg" or file_extension == ".jpeg":
        logging.info("reading jpg file {}".format(file_path))
        img = Image.open(file_path)
    elif file_extension == ".arw":
        logging.info("reading raw file {}".format(file_path))
        raw = rawpy.imread(file_path)
        rgb = raw.postprocess()
        img = Image.fromarray(rgb)
    else:
        raise Exception("unknown file extension {}".format(file_extension))

class PhotoStrip():
    def __init__(self, capture_id = None):
        self._capture_id = capture_id or datetime.datetime.now().isoformat()
        self._capture_dir = os.path.join("capture", self._capture_id)

        os.makedirs(self._capture_dir, exist_ok=True)

    def capture_files(self, camera)
        """take photos and create strip"""
        logging.info("capturing")

        final_image_path = os.path.join(self._capture_dir, "final.jpg")
        print_image_path = os.path.join(self._capture_dir, "final_print.jpg")

        captures = []

        for index, _ in enumerate(self._template_layout):
            countdown()
            logging.info("capturing photo {}".format(index))
            captures.append(self._camera.capture())

        logging.info("captured!")

        files = []
        for index, capture in enumerate(captures):
            logging.info("saving {}".format(capture.name))
            filename, file_extension = os.path.splitext(capture.name)
            saved_path = os.path.join(self._capture_dir, "image_{}{}".format(index, file_extension))
            self._camera.save(capture, saved_path)
            files.append(saved_path)

        return files

def create_img_from_template(self, files, template):
    logging.info("filling template")
    assert (len(files) == len(self._template_layout)), "files don't match template slots"

    final = self._template_image.copy()
    for index, layout in enumerate(self._template_layout):
        logging.info("adding photo {}".format(index))
        saved_path = files[index]
        for size, position in layout:
            img = read_file(saved_path)
            resized = ImageOps.fit(
                image=img,
                size=size,
                method=Image.ANTIALIAS,
            )
            final.paste(resized, position)

    return final

def main():
    """main"""
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s',
        level=logging.WARNING,
    )

    generator = PhotoStripGenerator(TEMPLATE_STRIPS)
    printer = get_printer()

    stored_exception = None
    capturing = False
    while True:
        try:
            if stored_exception:
                break
            wait_for_input()
            capturing = True
            files = generator.capture_files()

            # https://github.com/abelits/canon-selphy-print/blob/master/print-selphy-postcard
            printable_image = Image.new("RGB", (1248, 1872))
            printable_image.paste(final, (34, 46))
            printable_image.save(print_image_path, "JPEG", quality=97)

            final.convert("RGB").save(final_image_path, "JPEG", quality=90)

            logging.info("done")
            return (final_image_path, print_image_path)

            #if printer:
            #    printer.print_file(final_image_path)
            capturing = False
        except KeyboardInterrupt:
            if capturing:
                stored_exception = sys.exc_info()
            else:
                break


if __name__ == "__main__":
    main()
