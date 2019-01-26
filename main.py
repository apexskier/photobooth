import argparse
import logging
from os import path
import signal
import subprocess
import sys
import math
import time

import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from socketIO_client import SocketIO, BaseNamespace
from piVideoStream import PiVideoStream

# enable safe shutdown with ctl+c
global running
running = True

def signal_handler(signal, frame):
    global running
    running = False
    print("received signal, quitting")

signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser(description='Raspberry Pi photo booth')
parser.add_argument('--preview', action='store_true', help='Show a preview of the video feed')
parser.add_argument('--fps', action='store_true', help='Show an fps stat')
args = parser.parse_args()

logging.basicConfig(format='[%(levelname)s|%(asctime)s] %(message)s', level=logging.WARNING, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger('photobooth')
logger.setLevel(logging.INFO)

resolution = (640, 480)

current_dir = path.dirname(__file__)
face_cascade = cv2.CascadeClassifier(path.join(current_dir, 'haarcascade_frontalface_default.xml'))

def shift_point(pt, x, y):
    return (pt[0] + x, pt[1] + y)

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

class RateLimit(object):
    """
    Initialize with a function to be called. Calling this object calls the
    function a maximum of once every min_time.
    """
    def __init__(self, func, min_time=1):
        self.min_time = min_time
        self.func = func
        self.last_called = 0 # forever ago

    def __call__(self, *args, **kwargs):
        now = time.time()
        if now - self.last_called > self.min_time:
            self.func(*args, **kwargs)
            self.last_called = now

class WaitLimit(RateLimit):
    """
    Same functionality as RateLimit, but it sets timeout every time called.
    This means the delay between any execution is greater than time.
    """
    def __call__(self, *args, **kwargs):
        now = time.time()
        if now - self.last_called > self.min_time:
            self.func(*args, **kwargs)
        self.last_called = now

class Fps(object):
    _last_frame_time = None
    _frame_times = []

    def frame(self, image, now, first_frame):
        if not first_frame:
            frame_time = now - self._last_frame_time
            fps = 1 / frame_time

            self._frame_times.append(fps)
            self._frame_times = self._frame_times[-200:]

            cv2.rectangle(
                    img = image,
                    pt1 = (0, resolution[1] - 12),
                    pt2 = (32, resolution[1]),
                    color = (20, 20, 20),
                    thickness = cv2.FILLED,
                )
            cv2.putText(
                    img = image,
                    text = "{:5.0f} FPS".format(sum(self._frame_times) / float(len(self._frame_times))),
                    org = (0, resolution[1] - 4),
                    color = (255, 255, 255),
                    fontFace = cv2.FONT_HERSHEY_PLAIN,
                    fontScale = 0.4,
                )
        self._last_frame_time = now


class Faces(object):
    last_seen_face_at = 0
    first_saw_face_at = 0
    number_of_current_faces = 0

    def __init__(self, on_face):
        self.on_face = on_face

    def frame(self, image, now, first_frame):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # img[y: y + h, x: x + w]

        # face detection
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        num_faces = len(faces)
        if num_faces:
            if args.preview:
                for (x, y, w, h) in faces:
                    cv2.rectangle(preview, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Record some data about the face being seen
            self.last_seen_face_at = now
            if not self.number_of_current_faces:
                self.first_saw_face_at = now
            if self.number_of_current_faces != num_faces:
                logger.info('{} face{} found'.format(num_faces, '' if num_faces == 1 else 's'))
            self.number_of_current_faces = num_faces

            if self.on_face:
                self.on_face()
        else:
            # timeout for a face to really be gone
            # this accounts for not recognizing a face for a frame or two at a time
            if now - self.last_seen_face_at > 1:
                if self.number_of_current_faces:
                    logger.info('face lost')
                self.number_of_current_faces = 0

class Countdown():
    active = False

    def start(self, duration, callback):
        self.duration = duration
        self.active = True
        self.ends_at = time.time() + self.duration
        self.callback = callback

    def frame(self, image, now, first_frame):
        if self.active:
            time_left = self.ends_at - now

            if time_left < 0:
                self.active = False
                self.callback()
            else:
                cv2.putText(
                        img = image,
                        text = "{:d}".format(min(self.duration, int(math.floor(time_left)) + 1)),
                        org = (int(resolution[0] / 2), int(resolution[1] / 2)),
                        color = (55, 55, 255),
                        fontFace = cv2.FONT_HERSHEY_PLAIN,
                        fontScale = 2,
                    )

class PhotoStrip():
    last_image = None
    margin = 20

    def __init__(self):
        self.reset()
        self.thumb_dimensions = (int(resolution[0] / 2) - self.margin, int(resolution[1] / 2) - self.margin)

    def reset(self):
        self.stored_images = []

    def snap(self):
        if self.last_image is not None:
            self.stored_images.append(image)

    def frame(self, image, now, first_frame):
        self.last_image = image.copy()
        for i, snap in enumerate(self.stored_images):
            thumbnail = cv2.resize(snap, self.thumb_dimensions)
            start_index_y = self.margin
            start_index_x = self.margin
            image[
                    start_index_y:start_index_y + thumbnail.shape[0],
                    start_index_x:start_index_x + thumbnail.shape[1]
                ] = thumbnail

class PhotoBooth():
    def __init__(self):
        self.reset()

    def frame(self, image, now, first_frame):
        self.photostrip.frame(image, now, first_frame)
        self.countdown.frame(image, now, first_frame)

        if self.done:
            cv2.putText(
                    img = image,
                    text = "Done",
                    org = (int(resolution[0] / 2), int(resolution[1] / 2)),
                    color = (55, 255, 255),
                    fontFace = cv2.FONT_HERSHEY_PLAIN,
                    fontScale = 3,
                )

    def start(self):
        if not self.active:
            self.active = True
            self.countDownPhoto()

    def reset(self):
        self.active = False
        self.done = False
        self.photos = 0
        self.countdown = Countdown()
        self.photostrip = PhotoStrip()

    def countDownPhoto(self):
        if self.photos < 3:
            self.countdown.start(3, self.takePhoto)
            self.photos += 1
        else:
            self.done = True

    def takePhoto(self):
        self.photostrip.snap()
        self.countDownPhoto()

# continous data
first_frame = True

vs = PiVideoStream(resolution=resolution)
logger.info('initializing video...')
vs.start()
time.sleep(1)

pb = PhotoBooth()

fps = Fps()
faces = Faces(lambda: pb.start())

def stop():
    print("quitting")
    vs.stop()
    cv2.destroyAllWindows()

while running:
    try:
        now = time.time()

        image = vs.read()

        if args.preview:
            preview = image.copy()

        #faces.frame(preview, now, first_frame)
        pb.frame(preview, now, first_frame)

        if args.fps:
            fps.frame(preview, now, first_frame)

        if args.preview:
            cv2.imshow('Preview', preview)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

        first_frame = False
    except Exception as e:
        stop()
        raise e

stop()

