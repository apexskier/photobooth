#!/bin/bash

echo "photostrip start" >> /home/pi/photostrip/photostrip.log
LOGLEVEL=INFO /home/pi/.virtualenvs/photostrip/bin/python /home/pi/photostrip/src/capture.py >> /home/pi/photostrip/photostrip.log
echo "photostrip exit" >> /home/pi/photostrip/photostrip.log
