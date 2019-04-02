"""gphoto2 Camera abstraction"""

import logging
import os
import gphoto2 as gp

class Camera():
    """gphoto2 Camera abstraction"""

    def __init__(self):
        gp.check_result(gp.use_python_logging())

        self._camera = gp.Camera()

    def __enter__(self):
        logging.info("initializing camera")
        self._camera.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("cleaning up camera")
        self._camera.exit()

    def capture(self):
        """Capture an image as fast as possible. Returns an object used in save"""
        return self._camera.capture(gp.GP_CAPTURE_IMAGE)

    def save(self, capture, file_path):
        """Save a previously captured image to the file system"""
        _, file_extension = os.path.splitext(capture.name)
        file_path_without_extension, _ = os.path.splitext(file_path)
        camera_file = self._camera.file_get(
            capture.folder,
            capture.name,
            gp.GP_FILE_TYPE_NORMAL
        )
        final_path = file_path_without_extension + file_extension
        camera_file.save(file_path_without_extension + file_extension)

        del camera_file

        return final_path
