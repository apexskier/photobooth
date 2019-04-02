import logging

from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero import Device, Button, LED, PWMLED

# Set the default pin factory to a mock factory
Device.pin_factory = MockFactory(pin_class=MockPWMPin)

logger = logging.getLogger("lights")

class LedLightUi():
    def __init__(self):
        self._led = PWMLED(4)
    
    def __enter__(self):
        self.startup_animation()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutting_down()

    def startup_animation(self):
        logger.info("startup")
        self._led.blink(on_time=0.3, off_time=0.3, n=3)
        self._led.off()

    def ready_animation(self):
        logger.info("ready")
        self._led.pulse(fade_in_time=1, fade_out_time=1, background=True)

    def processing_animation(self):
        logger.info("processing")
        self._led.pulse(fade_in_time=0.5, fade_out_time=0.5, background=True)

    def countdown_animation(self, n):
        logger.info("countdown")
        self._led.blink(on_time=0.3, off_time=0.4, n=n)
        self._led.on()

    def complete_animation(self):
        logger.info("complete")
        self._led.blink(on_time=0.2, off_time=0.2, n=5)

    def shutting_down(self):
        logger.info("shutting down")
        self._led.off()