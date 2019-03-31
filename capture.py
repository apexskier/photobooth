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
from templates import TEMPLATE_SQUARE
from cli_input import wait_for_input

COUNTDOWN = 5

def countdown():
    """Display a countdown timer"""
    for i in reversed(range(0, COUNTDOWN)):
        print(i + 1)
        time.sleep(1)

def process_raw_file(file_path, size):
    """read a raw image file and convert to the format we'll insert into the template"""
    raw = rawpy.imread(file_path)
    rgb = raw.postprocess()
    img = Image.fromarray(rgb)
    return ImageOps.fit(
        image=img,
        size=size,
        method=Image.ANTIALIAS,
    )

class PhotoStripGenerator():
    """a generator for a specific photostrip template"""
    def __init__(self, template):
        self._camera = Camera()
        self._template_image = Image.open(template['file'])
        self._template_layout = template['layout']

    def capture(self):
        """take photos and create strip"""
        capture_id = datetime.datetime.now().isoformat(timespec="seconds")
        capture_dir = os.path.join("capture", capture_id)

        os.makedirs(capture_dir, exist_ok=True)

        def fill_template(files):
            assert (len(files) == len(self._template_layout)), "files don't match template slots"

            final = self._template_image.copy()
            for index, layout in enumerate(self._template_layout):
                saved_path = files[index]
                for size, position in layout:
                    final.paste(process_raw_file(saved_path, size), position)

            final.convert("RGB").save(os.path.join(capture_dir, "final.jpg"), "JPEG", quality=90)

        captures = []

        for _ in self._template_layout:
            countdown()
            captures.append(self._camera.capture())

        print("captured!")

        files = []
        for capture in captures:
            saved_path = os.path.join(capture_dir, os.path.basename(capture.name))
            self._camera.save(capture, saved_path)
            files.append(saved_path)

        fill_template(files)

        print("done")

def main():
    """main"""
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s',
        level=logging.WARNING,
    )

    generator = PhotoStripGenerator(TEMPLATE_SQUARE)

    stored_exception = None
    capturing = False
    while True:
        try:
            if stored_exception:
                break
            wait_for_input()
            capturing = True
            generator.capture()
            capturing = False
        except KeyboardInterrupt:
            if capturing:
                stored_exception = sys.exc_info()
            else:
                break


if __name__ == "__main__":
    main()
