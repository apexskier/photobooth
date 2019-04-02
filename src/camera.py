"""gphoto2 Camera abstraction"""

import logging
import os
import gphoto2 as gp
import time

logger = logging.getLogger("camera")

gp_logger = logger.getChild("gp")

def _log_callback(level, domain, string, data=None):
    log_level = logging.WARNING
    if level == gp.GP_LOG_ERROR:
        log_level = logging.WARNING
    elif level == gp.GP_LOG_DEBUG:
        log_level = logging.DEBUG
    elif level == gp.GP_LOG_VERBOSE:
        log_level = logging.DEBUG - 3
    elif level == gp.GP_LOG_DATA:
        log_level = logging.DEBUG - 6

    if string in (
        b"'libusb_claim_interface (port->pl->dh, port->settings.usb.interface)' failed: Access denied (insufficient permissions) (-3)"
    ):
        return

    gp_logger.log(log_level, string.decode("utf-8"))

class Camera():
    """gphoto2 Camera abstraction"""

    def __init__(self):
        gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, _log_callback))
        self._camera = gp.Camera()

    def __enter__(self):
        logger.info("initializing camera")
        initialized = False
        while not initialized:
            try:
                self._camera.init()
                initialized = True
            except gp.GPhoto2Error as err:
                if err.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                    time.sleep(2)
                elif err.code == gp.GP_ERROR_IO_USB_CLAIM:
                    time.sleep(2)
                elif err.code == -1:
                    logger.warn("Something bad happened")
                    time.sleep(5)
                else:
                    raise err
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("cleaning up camera")
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
