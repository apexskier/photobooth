from gpiozero import LED, Button

# Set the default pin factory to a mock factory
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory, MockPin
# Device.pin_factory = MockFactory(pin_class=MockPin)

button = Button(21)

def wait_for_input():
    button.wait_for_press()
    button.wait_for_release()
