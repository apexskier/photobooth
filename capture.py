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
    _, file_extension = os.path.splitext(file_path)
    if file_extension in ('.jpg', '.jpeg'):
        logging.info("reading jpg file {}".format(file_path))
        img = Image.open(file_path)
    elif file_extension == ".arw":
        logging.info("reading raw file {}".format(file_path))
        raw = rawpy.imread(file_path)
        rgb = raw.postprocess()
        img = Image.fromarray(rgb)
    else:
        raise Exception("unknown file extension {}".format(file_extension))
    return img

class PhotoStrip():
    def __init__(self, capture_id = None):
        self._capture_id = capture_id or datetime.datetime.now().isoformat()
        self.capture_dir = os.path.join("capture", self._capture_id)

        os.makedirs(self.capture_dir, exist_ok=True)

    def capture_files(self, camera, count):
        """take photos and create strip"""
        logging.info("capturing")

        captures = []

        for index in range(count):
            countdown()
            logging.info("capturing photo {}".format(index))
            captures.append(camera.capture())

        logging.info("captured!")

        files = []
        for index, capture in enumerate(captures):
            logging.info("saving {}".format(capture.name))
            _, file_extension = os.path.splitext(capture.name)
            saved_path = os.path.join(self.capture_dir, "image_{}{}".format(index, file_extension))
            camera.save(capture, saved_path)
            files.append(saved_path)

        return files
    
    def read_files(self, count):
        logging.info("reading")

        captures = []

        files = []
        for file_path in os.listdir(self.capture_dir):
            if file_path.startswith("image_"):
                files.append(file_path)

        files.sort()
        return [os.path.join(self.capture_dir, f) for f in files]
    
    def save_final_img(self, img, name):
        final_image_path = os.path.join(self.capture_dir, "{}.jpg".format(name))
        img.convert("RGB").save(final_image_path, "JPEG", quality=90)

_CACHED_TEMPLATES = {}
def get_template_image(template):
    if not _CACHED_TEMPLATES.get(template['file'], None):
        _CACHED_TEMPLATES[template['file']] = Image.open(template['file'])
    return _CACHED_TEMPLATES[template['file']]

def create_img_from_template(files, template):
    template_image = get_template_image(template)
    template_layout = template['layout']

    logging.info("filling template")
    assert (len(files) == len(template_layout)), "files don't match template slots"

    final = template_image.copy()
    for index, layout in enumerate(template_layout):
        logging.info("adding photo {}".format(index))
        img = read_file(files[index])
        for size, position in layout:
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

    printer = get_printer()
    camera = Camera()

    stored_exception = None
    capturing = False
    while True:
        try:
            if stored_exception:
                break
            wait_for_input()
            capturing = True

            # ps = PhotoStrip("2019-04-01T16:50:31.213095")
            ps = PhotoStrip()
            logging.info("starting")
            files = ps.capture_files(camera, len(TEMPLATE_STRIPS['layout']))
            logging.info("using template {}".format(TEMPLATE_STRIPS['name']))
            img = create_img_from_template(files, TEMPLATE_STRIPS)
            logging.info("saving")
            ps.save_final_img(img, TEMPLATE_STRIPS['name'])

            if printer:
                logging.info("printing")

                # https://github.com/abelits/canon-selphy-print/blob/master/print-selphy-postcard
                printable_image = Image.new("RGB", (1248, 1872))
                printable_image.paste(img, (34, 46))
                printable_image.save("./toprint.jpg", "JPEG", quality=97)

                printer.print_file("./toprint.jpg")

            capturing = False
        except KeyboardInterrupt:
            if capturing:
                stored_exception = sys.exc_info()
            else:
                break


if __name__ == "__main__":
    main()
