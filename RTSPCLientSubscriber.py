
# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2 # Opencv-python

def show_camera():

	# cv2.VideoCapture: This is an OpenCV class used to capture video from cameras or video files. Here, it is used to capture video from an RTSP stream using 	#GStreamer.
	 
	# "rtspsrc location=rtsp://10.11.3.64:8554/stream latency=0 ! decodebin ! videoconvert ! appsink": This is a GStreamer pipeline string passed to OpenCV for 	#capturing the video stream.
 
	# rtspsrc: This GStreamer element retrieves video data from an RTSP source.

	# location=rtsp://10.11.3.64:8554/stream: This parameter specifies the URL of the RTSP stream to be accessed. In this case, the stream is located at 	#rtsp://10.11.3.64:8554/stream.

	# latency=0: This parameter sets the latency of the RTSP source. A latency of 0 aims for minimal delay, which is important for real-time streaming 	#applications.
 
	# decodebin: This GStreamer element automatically detects and selects the appropriate decoder for the incoming video stream. It dynamically links to the 	#correct decoder based on the stream's format and codecs.
 
	# videoconvert: This GStreamer element converts video frames to a format suitable for further processing or display. It ensures compatibility with the appsink 	#element.
 
	# appsink: This GStreamer element allows the GStreamer pipeline to output video frames to the application, in this case, OpenCV. It makes the frames available 	#to OpenCV for further processing.

	# cv2.CAP_GSTREAMER: This flag tells OpenCV to use GStreamer as the backend for video capture. It enables the use of GStreamer pipelines within OpenCV's 	#VideoCapture function.

    vcap = cv2.VideoCapture("rtspsrc location=rtsp://10.11.3.64:8554/stream latency=0 ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

    print(vcap.isOpened())  # this line is purely for debugging, it checks if the stream is opened

    while (1):
        ret, frame = vcap.read() 		# it reads a frame from the video stream
        cv2.imshow('VIDEO', frame)              # it shows the frame just taken opening a window
        keyCode = cv2.waitKey(10) & 0xFF        # chekc if the user pressed "q", in order to quit and stop the program
        if keyCode == 27 or keyCode == ord('q'):
            vcap.release()
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    show_camera()
