import logging
import math
import time

from gpiozero import Button, LED, PWMLED
from gpiozero.threads import GPIOThread

# Set the default pin factory to a mock factory
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory, MockPWMPin
# Device.pin_factory = MockFactory(pin_class=MockPWMPin)

logger = logging.getLogger("lights")

class MyPWMLED(PWMLED):
    def ease(self, easing_function, duration=None):
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._ease,
            args=(
                easing_function,
                duration,
            )
        )
        self._blink_thread.start()

    def _ease(self, easing_function, duration):
        start = now = time.time()
        if duration:
            end = now + duration

        while not duration or now < end:
            v = easing_function(now - start)
            self._write(v)
            if self._blink_thread.stopping.wait(0.01):
                break
            now = time.time()

class LedLightUi():
    def __init__(self):
        self._led = MyPWMLED(pin=13, initial_value=0)

    def __enter__(self):
        self.startup_animation()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutting_down()

    def startup_animation(self):
        logger.info("startup")
        self._led.blink(on_time=0.3, off_time=0.1)

    def ready_animation(self):
        logger.info("ready")
        self._led.on()
        self._led.ease(easing_function = lambda ms: (math.sin((ms * 1.2) + (math.pi / 2)) * 0.8 + 1.2) / 2)

    def processing_animation(self):
        logger.info("processing")
        self._led.on()
        self._led.ease(easing_function = lambda ms: (math.sin((ms * 4) + (math.pi / 2)) + 1) / 2)

    def countdown_animation(self, n):
        logger.info("countdown")
        self._led.blink(on_time=0.3, off_time=0.7, n=n, background=False)
        self._led.on()

    def complete_animation(self):
        logger.info("complete")
        self._led.blink(on_time=0.2, off_time=0.2, n=5, background=False)

    def shutting_down(self):
        logger.info("shutting down")
        self._led.off()
