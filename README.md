# Photobooth

This is a little photobooth application for my wedding (and more, hopefully).

It's built to be installed on a raspberry pi and uses a physical arcade button and an LED for the user interface (no screen).

I use a Sony Alpha 6300 camera, but it should work with any camera that supports USB control via [gphoto2](http://www.gphoto.org/).

My printer is a [Canon SELPHY CP1300](https://www.usa.canon.com/internet/portal/us/home/products/details/printers/mobile-compact-printer/cp1300-bkn), but it's not required.

## Setup

- install python 3+
- `sudo apt install libraw-dev` (for pyraw support)
  - note: I ended up changing my camera to only capture JPEG, since raw processing and transfer is really slow and was causing issues
- create a virtualenv
- `pip install -r requirements.txt`
  - note: numpy is slow and painful to install
- to autostart on boot, I used cron. See the `crontab` file for an example

## Usage

- When started, light will blink on and off while initalizing
- Light will slowly pulse brighter and dimmer when ready
- Light will flash 5 times as a countdown for each photo
- Light will pulse on and off quickly while processing
- Light will flash quickly when complete, then resume slow pulsing

### Camera setup

- Ensure Camera > 1 > "Quality" is not set to RAW
- Ensure Toolbox > 4 > "USB Connection" is set to "PC Remote"
- Ensure camera is on single shot mode

### Printer issues

- If the printer sleeps, turn it back on. It will process jobs sent to it while asleep
- If the printer runs out of ink/paper, replace both

## Adding templates

Custom templates can be added and used pretty easily. Take a look at `src/templates.py`. You'll create a base image file and describe
the plaes images will be written into.
