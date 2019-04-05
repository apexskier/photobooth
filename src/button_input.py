from gpiozero import LED, Button

button = Button(21)

def wait_for_input():
    button.wait_for_press()
    button.wait_for_release()
