from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2

class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=30):
        self._camera = PiCamera()
        self._camera.resolution = resolution
        self._camera.framerate = framerate
        self._rawCapture = PiRGBArray(self._camera, size=resolution)
        self._stream = self._camera.capture_continuous(
                self._rawCapture,
                format="bgr",
                use_video_port=True,
            )

        self._frame = None
        self._stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()

    def update(self):
        for f in self._stream:
            self._frame = f.array
            self._rawCapture.truncate(0)

            if self._stopped:
                self._stream.close()
                self._rawCapture.close()
                self._camera.close()
                return

    def read(self):
        return self._frame

    def stop(self):
        self._stopped = True
