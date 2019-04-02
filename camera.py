"""gphoto2 Camera abstraction"""

import gphoto2 as gp

class Camera():
    """gphoto2 Camera abstraction"""

    def __init__(self):
        gp.check_result(gp.use_python_logging())

        self._camera = gp.Camera()
        self._camera.init()

    def __del__(self):
        self._camera.exit()

    def capture(self):
        """Capture an image as fast as possible. Returns an object used in save"""
        return self._camera.capture(gp.GP_CAPTURE_IMAGE)

    def save(self, capture, file_path):
        """Save a previously captured image to the file system"""
        camera_file = self._camera.file_get(
            capture.folder,
            capture.name,
            gp.GP_FILE_TYPE_NORMAL
        )
        camera_file.save(file_path)

        del camera_file
