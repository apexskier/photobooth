"""gphoto2 Camera abstraction"""

import gphoto2 as gp

class Camera():
    """gphoto2 Camera abstraction"""

    def __init__(self):
        gp.check_result(gp.use_python_logging())
        self._camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self._camera))

    def __del__(self):
        gp.check_result(gp.gp_camera_exit(self._camera))

    def capture(self):
        """Capture an image as fast as possible. Returns an object used in save"""
        file_path = gp.check_result(gp.gp_camera_capture(self._camera, gp.GP_CAPTURE_IMAGE))
        return file_path

    def save(self, capture, file_path):
        """Save a previously captured image to the file system"""
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self._camera,
            capture.folder,
            capture.name,
            gp.GP_FILE_TYPE_NORMAL
        ))
        gp.check_result(gp.gp_file_save(camera_file, file_path))
