from gpiozero import LED, Button

button = Button(2)

def wait_for_input():
    while True:
        button.wait_for_press()
        button.wait_for_release()