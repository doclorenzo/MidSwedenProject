# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

from ultralytics import YOLO
import cv2
import math

model = YOLO('yolov8n.pt')
def show_camera():
    infile = open("filename.txt", 'w')

    vcap = cv2.VideoCapture("rtspsrc location=rtsp://10.11.3.64:8554/stream latency=0 ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

    print(vcap.isOpened())

    while (1):
        ret, frame = vcap.read()
        results = model(frame, stream=True)  # before showing it, it "gives the image to Yolo" to detect obejcts in the array results
        for r in results:  # iterate trhought the found boxes
            boxes = r.boxes

            for box in boxes:  # takes the box
                # bounding box
                x1, y1, x2, y2 = box.xyxy[0]  # takes the coordinates
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values the coord.

                # put box in cam
                # create rectangle function arguments: image / coordinated start, end / color of rectangle / thickness
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # confidence
                confidence = math.ceil((box.conf[0] * 100)) / 100  # caluatethe accuracy
                infile.write(f"{confidence}\n")
                print("Confidence --->", confidence)
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2
                text = r.names[box.cls[0].item()]  # name of class of object
                text += f" {confidence}"  # adds the conficende to the type of object string took before

                cv2.putText(frame, text, org, font, fontScale, color, thickness)  # creste the text to show
        cv2.imshow('VIDEO', frame)
        keyCode = cv2.waitKey(10) & 0xFF
        # Stop the program on the ESC key or 'q'
        if keyCode == 27 or keyCode == ord('q'):
            vcap.release()
            cv2.destroyAllWindows()
            infile.close()
            break

if __name__ == "__main__":
    show_camera()


