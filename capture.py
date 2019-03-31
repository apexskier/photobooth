"""
Photobooth capture script
"""

import asyncio
import logging
import os
import datetime

import rawpy
from PIL import Image, ImageOps
from camera import Camera
from templates import TEMPLATE_SQUARE

COUNTDOWN = 5

async def countdown():
    """Display a countdown timer"""
    for i in reversed(range(0, COUNTDOWN)):
        print(i + 1)
        await asyncio.sleep(1)

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

async def main():
    """main"""
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s',
        level=logging.WARNING,
    )

    capture_id = datetime.datetime.now().isoformat(timespec="seconds")
    capture_dir = os.path.join("capture", capture_id)

    os.makedirs(capture_dir, exist_ok=True)

    template_image = Image.open(TEMPLATE_SQUARE['file'])
    template_layout = TEMPLATE_SQUARE['layout']

    def fill_template(files):
        assert (len(files) == len(template_layout)), "files don't match template slots"

        final = template_image.copy()
        for index, layout in enumerate(template_layout):
            saved_path = files[index]
            for size, position in layout:
                final.paste(process_raw_file(saved_path, size), position)

        final.convert("RGB").save(os.path.join(capture_dir, "final.jpg"), "JPEG", quality=90)

    with Camera() as camera:
        print("starting")

        captures = []

        for _ in template_layout:
            # await countdown()
            captures.append(camera.capture())

        print("captured!")

        files = []
        for capture in captures:
            saved_path = os.path.join(capture_dir, os.path.basename(capture.name))
            camera.save(capture, saved_path)
            files.append(saved_path)

        fill_template(files)

        print("done")

if __name__ == "__main__":
    asyncio.run(main())
