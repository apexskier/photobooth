#!/bin/bash

ID=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

WORKING_DIR="./capture/$ID"
mkdir -p "$WORKING_DIR" 

echo "capturing..."

for i in {1..3}
do
    sleep 5
    gphoto2 --capture-image-and-download --keep --stdout > "./${WORKING_DIR}/image_${i}.arw"
done

echo "processing..."

echo "  converting to jpg..."

for i in {1..3}
do
    RAW_FILE="./${WORKING_DIR}/image_${i}.arw"
    JPG_FILE="./${WORKING_DIR}/image_${i}.jpg"
    sips -s format jpeg "$RAW_FILE" --out "$JPG_FILE"
done

echo "  cropping/resizing..."

for i in {1..3}
do
    FULL_SIZE_FILE="./${WORKING_DIR}/image_${i}.jpg"
    SMALL_SIZE_FILE="./${WORKING_DIR}/image_${i}_small.jpg"
    convert "$FULL_SIZE_FILE" -resize 660x660^ -gravity center -extent 660x660 -quality 90 "$SMALL_SIZE_FILE"
done

echo "  combining..."

TEMPLATE_FILE="./4x4.png"
FINAL_FILE="./${WORKING_DIR}/final.jpg"

TOP_LEFT_FILE="./${WORKING_DIR}/image_1_small.jpg"
convert "$TEMPLATE_FILE" "$TOP_LEFT_FILE" -geometry +40+40 -composite "$FINAL_FILE"

TOP_RIGHT_FILE="./${WORKING_DIR}/image_2_small.jpg"
convert "$FINAL_FILE" "$TOP_RIGHT_FILE" -geometry +740+40 -composite "$FINAL_FILE"

BOT_LEFT_FILE="./${WORKING_DIR}/image_3_small.jpg"
convert "$FINAL_FILE" "$BOT_LEFT_FILE" -geometry +40+740 -composite "$FINAL_FILE"

open $FINAL_FILE