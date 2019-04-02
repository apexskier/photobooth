def wait_for_input():
    while True:
        text = input("<Enter> to capture\n")
        if text == "":
            return
        else:
            print("I didn't understand:", text)

