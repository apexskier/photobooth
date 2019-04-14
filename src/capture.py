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
from button_input import wait_for_input
from printer import get_printer
from lights import LedLightUi
from upload import Uploader

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=os.environ.get("LOGLEVEL", "INFO"),
    stream=sys.stdout,
)

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

    def capture_files(self, lights, camera, count):
        """take photos and create strip"""
        logging.info("capturing")

        captures = []

        for index in range(count):
            lights.countdown_animation(5) # 5th light captures
            logging.info("capturing photo {}".format(index))
            captures.append(camera.capture())
            time.sleep(1) # try to avoid i/o issues

        logging.info("captured!")

        files = []
        for index, capture in enumerate(captures):
            logging.info("saving {}".format(capture.name))
            saved_path = os.path.join(self.capture_dir, "image_{}".format(index))
            files.append(camera.save(capture, saved_path))

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
        final_image_path = os.path.join(self.capture_dir, "{}_{}.jpg".format(name, self._capture_id))
        img.convert("RGB").save(final_image_path, "JPEG", quality=90)
        return final_image_path

_CACHED_TEMPLATES = {}
def get_template_image(template):
    if not _CACHED_TEMPLATES.get(template['file'], None):
        _CACHED_TEMPLATES[template['file']] = Image.open(template['file'])
    return _CACHED_TEMPLATES[template['file']]

def create_img_from_template(files, template):
    logging.info("using template {}".format(template['name']))
    template_image = get_template_image(template)
    template_layout = template['layout']

    logging.info("filling template")
    assert (len(files) == len(template_layout)), "files don't match template slots"

    final = template_image.copy()
    for index, layout in enumerate(template_layout):
        file_path = files[index]
        logging.info("adding photo {}: ".format(index, file_path))
        img = read_file(file_path)
        for size, position in layout:
            resized = ImageOps.fit(
                image=img,
                size=size,
                method=Image.ANTIALIAS,
            )
            final.paste(resized, position)

    return final

def print_image(printer, img):
    logging.info("printing to {}".format(printer.name))

    # initially based on https://github.com/abelits/canon-selphy-print/blob/master/print-selphy-postcard
    base_image_size = (1190, 1760)
    # assert base_image_size == template image dimensions, "template image must be the exact right size"
    top_left_inset = (28, 52)
    bot_right_inset = (36, 130)

    printable_image = Image.new(
        "RGB",
        (
            base_image_size[0] + top_left_inset[0] + bot_right_inset[0],
            base_image_size[1] + top_left_inset[1] + bot_right_inset[0]
        )
    )
    printable_image.paste(img, top_left_inset)
    printable_image.save("./toprint.jpg", "JPEG", quality=97)

    printer.print_file("./toprint.jpg")

def main():
    """main"""
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s',
        level=logging.WARNING,
    )

    keyboard_interrupt = None
    capturing = False

    try:
        printer = get_printer()
        if not printer:
            logging.warn("No printer found")
        else:
            logging.info("Found printer {}".format(printer.name))

        uploader = Uploader()

        with LedLightUi() as lights, Camera() as camera:
            #logging.info("testing camera")
            #test_capture = camera.capture(),
            #time.sleep(1)
            #test_path = camera.save(
            #    test_capture,
            #    os.path.join("capture", "test_{}".format(datetime.datetime.now().isoformat()))
            #)
            #if not test_path.endswith('.jpg'):
            #    logging.warn("camera's returning raw files, {}".format(os.splitext(test_path)[1]))

            logging.info("starting capture loop")
            while not keyboard_interrupt:
                lights.ready_animation()
                wait_for_input()
                capturing = True

                try:
                    ps = PhotoStrip()

                    files = ps.capture_files(lights, camera, len(TEMPLATE_STRIPS['layout']))

                    lights.processing_animation()

                    strip_img = create_img_from_template(files, TEMPLATE_STRIPS)
                    ps.save_final_img(strip_img, TEMPLATE_STRIPS['name'])

                    if printer:
                        print_image(printer, strip_img)

                    square_img = create_img_from_template(files, TEMPLATE_SQUARE)
                    square_path = ps.save_final_img(square_img, TEMPLATE_SQUARE['name'])
                    uploader.upload_file(square_path)

                except Exception as err:
                    logging.error(err)
                    logging.warn("continuing")

                lights.complete_animation()
                capturing = False
    except KeyboardInterrupt:
        if capturing:
            keyboard_interrupt = sys.exc_info()


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logging.error("Shutting down due to error")
        print(err)
