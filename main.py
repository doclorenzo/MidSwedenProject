# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

from ultralytics import YOLO #importing YOLO
import cv2
import math

model = YOLO('yolov8m.pt') #Import a Yolo model, in this case Yolov8 medium
def show_camera():

    # cv2.VideoCapture: This is an OpenCV class used to capture video from cameras or video files. Here, it is used to capture video from an RTSP stream using GStreamer	 
	# "rtspsrc location=rtsp://10.11.3.64:8554/stream latency=0 ! decodebin ! videoconvert ! appsink": This is a GStreamer pipeline string passed to OpenCV for capturing the video stream.
	# rtspsrc: This GStreamer element retrieves video data from an RTSP source.
	# location=rtsp://10.11.3.64:8554/stream: This parameter specifies the URL of the RTSP stream to be accessed. In this case, the stream is located at rtsp://10.11.3.64:8554/stream.
	# latency=0: This parameter sets the latency of the RTSP source. A latency of 0 aims for minimal delay, which is important for real-time streaming applications.
	# decodebin: This GStreamer element automatically detects and selects the appropriate decoder for the incoming video stream. It dynamically links to the correct decoder based on the stream's format and codecs.
	# videoconvert: This GStreamer element converts video frames to a format suitable for further processing or display. It ensures compatibility with the appsink element.
	# appsink: This GStreamer element allows the GStreamer pipeline to output video frames to the application, in this case, OpenCV. It makes the frames available to OpenCV for further processing.
	# cv2.CAP_GSTREAMER: This flag tells OpenCV to use GStreamer as the backend for video capture. It enables the use of GStreamer pipelines within OpenCV's VideoCapture function.

    vcap = cv2.VideoCapture("rtspsrc location=rtsp://10.11.3.64:8554/stream latency=0 ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

    print(vcap.isOpened())

    while (1):
        ret, frame = vcap.read()
        
        # before showing the frame, it "gives it the Yolo model" to detect obejcts in the array results
        results = model(frame, stream=True)  
        
        for r in results:  # iterate till there are boxes
            boxes = r.boxes

            for box in boxes:  # takes the box
                # cretae bounding box
                x1, y1, x2, y2 = box.xyxy[0]  # takes the coordinates
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values the coord.

                # create rectangle function arguments: image / coordinated start, end / color of rectangle / thickness
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # confidence
                confidence = math.ceil((box.conf[0] * 100)) / 100  # caluatethe accuracy
                print("Confidence --->", confidence)  # print confidence fro dubugging matters
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX  
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2
                text = r.names[box.cls[0].item()]  # takes the semantic name of the detected object
                text += f" {confidence}"  # adds the conficende to the type of object string took before

                cv2.putText(frame, text, org, font, fontScale, color, thickness)  # creste the text to show above the bounding box
        cv2.imshow('VIDEO', frame)  #show the frame in a window
        keyCode = cv2.waitKey(10) & 0xFF
        # Stop the program on the ESC key or 'q'
        if keyCode == 27 or keyCode == ord('q'):
            vcap.release()
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    show_camera()


