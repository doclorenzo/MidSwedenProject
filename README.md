Installation Guide

1) List of components

In this section it will be presented a list of the hardware and software components used to implement the project

Hardware:

Jetson Orin Nano: 
GPU: 1024-core NVIDIA Ampere architecture GPU with 32 Tensor Cores,
CPU: 6-core Arm® Cortex®-A78AE v8.2 64-bit CPU 1.5MB L2 + 4MB L3  
RAM: 8GB 
CSI CAMERA: 2x MIPI CSI-2 22-pin Camera Connectors

Raspberry Pi Camera HQ:
Sensor: Sony IMX477R stacked, back-illuminated sensor
Resolution: 12.3 megapixels
Pixel Size: 1.55 µm x 1.55 µm
Lens Mount: C-mount (compatible with CS-mount with adapter)
Interface: MIPI CSI-2 (15-pin ribbon cable)
Maximum Frame Rate:1080p @ 30 fps, 720p @ 60 fps, Higher resolutions possible at lower frame rates 

15-pins to 22-pins converter
Firecell 

5.1.2 Software

Ubuntu 22.04, installed on both the JON and the Firecell
Gstreamer 
MediaMTX 
Python 
OpenCV 
YOLOv8 

Both hardware and software components will be described in detail in the next chapters, as well as their implementation and usage.

5.2 Connecting the Camera
The first step of the implementation concerns connecting the camera to the Jetson Orin Nano as follows

5.2.1 Selecting the camera pins 
A structured approach is necessary to implement the integration of video streaming. The data captured by the robot's cameras necessitates transmission to the VR headset via the RTSP protocol. This entails a sequential process beginning with the connection of cameras and the Jetson Orin Nano. The camera, which is a RaspberryPi Camera HQ has been connected to the cam slot: “cam0” of the board. This connection mandates a reconfiguration of the camera slot pins from IMX217 to the dual IMX477 specification, which is doable through the natively present configuration file at /opt/nvidia/jetson-io/jetson-io.py of the NVIDIA Board. In addition, in order to connect the camera to the board it is necessary to use a 15-pin to 22-pin conversion cable as shown in Fig 5.1. 

5.2.2 Testing camera connection
To check if the camera is well connected and the the whole process worked you can run this command: 
gst-launch-1.0 nvarguscamerasrc sensor_id=0 !  \  'video/x-raw(memory:NVMM),width=1920, height=1080,\ framerate=30/1' !nvvidconv flip-method=0 ! \ 'video/x-raw,width=960, height=540' ! nvvidconv ! \ nvegltransform ! nveglglessink -e

Here a brief explanation of the command:

gst-launch-1.0: This is the GStreamer command-line tool used to build and run pipelines.
nvarguscamerasrc sensor_id=0:
nvarguscamerasrc: This element captures video from the NVIDIA Argus camera.
sensor_id=0: Specifies the camera sensor to use (if there are multiple cameras).
!: This is a GStreamer separator indicating that the output of one element is being passed as the input to the next element.
'video/x-raw(memory
),width=1920, height=1080, framerate=30/1':
video/x-raw(memory
): Specifies the raw video format using NVMM (NVIDIA Memory Management).
width=1920, height=1080: Sets the resolution of the video stream.
framerate=30/1: Sets the frame rate to 30 frames per second.
nvvidconv flip-method=0:
nvvidconv: This element is used to convert video formats and resolutions.
flip-method=0: Specifies the method of flipping the video. 0 means no flip.
'video/x-raw,width=960, height=540':
video/x-raw: Specifies the raw video format.
width=960, height=540: Sets the new resolution for the video stream after conversion.
nvvidconv: Another instance of the video conversion element to handle the resolution change.
nvegltransform: This element handles transformations required for EGL (Embedded-System Graphics Library) operations.
nveglglessink:
nveglglessink: This element renders the video stream using EGL and OpenGL ES.
-e: Tells GStreamer to send an End-of-Stream (EOS) event after the pipeline has finished running.

To make the command work, it is first necessary to install Gstreamer.
This is just an example, as a matter of fact width and height can be modified, as well as other components of the pipeline.

Fig 5.1 CSI camera connected to JON 

5.3 Configure RTSP server on JON
 The RTSP server, in turn, has been realized through the MediaMTX library which is a ready-to-use and zero-dependency real-time media server and media proxy that allows to publish, read, proxy, record and playback video and audio streams. The server has been setted up locally on the board and it receives the video stream from the Gstreamer's RTSP Client that we discuss later. The first step is installing the server, there are four possible ways of doing it all available on the official documentation.
For this project we installed the server with the standalone binary process, so just downloading the asset file : mediamtx_v1.8.1_linux_arm64v8.tar.gz ,
which is the one compatible with the architecture of JON, extracting it in a directory and running the command ./mediamtx to start up the server.
To make the server work, we changed its configuration expanding the limitation on the usage of the RAM memory, from 1GB (the standard value) to 4GB, so that it is able to handle bigger portions of frames and letting the system to generally have a better and stable frame-rate. 
In order to expand the limitation on RAM usage we modified the file mediamtx.yml, (which is available in the same directory where the zip file has been extracted) at the line:
writeQueueSize: 1024, where we modified the value 1024 to 4096 (this value can be higher or lower, depending on the needs of the user, but it is mandatory to be a power of 2). The reason of this change in the settings of the server is that  during our tests, while the client was sending the video stream though, in the logs we noticed that many packets were lost or corrupted and couldn’t been handled properly by the server as shown in Fig 5.2, by researching on the official documentation of MediaMTX, we found that this problem can be solved by increasing the value of writeQueueSize.


Fig 5.2 Warning on RTSP server fix

This process is also available on the official documentation at: RTSP-specific features, Corrupted frames.
Once we applied the changes, we were able to start up the server running by the ./mediamtx command, which provides a functioning RTSP server, respectively: TCP/RTSP listener at port 8554, as shown in Fig 5.3.
As there can be other ports listening for UDP and UDP-Multicast simultaneously , ome could shut them down to make the system a bit lighter by changing the settings at  mediamtx.yml by modifying the line:
protocols: [udp, multicast, tcp] to protocols: [tcp]


Fig 5.3 RTSP server

5.4 Configure RTSP Client Publisher on JON 

The next step concerns creating an RTSP Client on the JON, which will take in input the video stream from the camera and publish it to the server. In order to combine those two goals, we used Gstreamer, which is an open-source multimedia framework that provides a pipeline-based architecture for creating, processing, and streaming audio and video content across various platforms and devices. It offers a flexible and modular approach for multimedia processing, enabling developers to build custom multimedia applications. After installing the Gstreamer package , and after a lot of tests, we created a perfect command defining a proper pipeline in order to accomplish the goal of sending the videostream to the server through RTSP:

gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! \ 'video/x-raw(memory:NVMM),width=1280, height=720, \ framerate=20/1' ! nvvidconv ! queue ! rtspclientsink \ location=rtsp://localhost:8554/stream 

A brief explanation of  the commands is as follows:
gst-launch-1.0: This is the GStreamer command-line tool used to build and run multimedia pipelines.
nvarguscamerasrc: This is a GStreamer element that captures video from NVIDIA's Argus camera interface, used for interfacing with the Raspberry Pi camera.
sensor_id=0: This parameter specifies the ID of the camera sensor to use. In this case, it's set to 0, indicating the first camera sensor (cam0)
'video/x-raw(memory:NVMM),width=1280, height=720, framerate=20/1': This is a caps filter specifying the desired format for the video stream. It specifies that the video should be in raw format, encoded in 10bit-h265 algorithm,  with a width of 1280 pixels, height of 720 pixels, and a framerate of 20 frames per second. Obviously those parameter can be changed, here we show just an example. The memory type is specified as NVMM, indicating NVIDIA's Memory Manager.
nvvidconv: This is a GStreamer element used for video conversion. It converts the raw video format to a format suitable for further processing or encoding.
queue: This element is used for buffering and synchronization within the pipeline. It helps to smooth out the flow of data between elements.
rtspclientsink location=rtsp://localhost:8554/stream:This element is a GStreamer sink that streams the video over RTSP . It specifies the destination location of the RTSP stream, which in this case is rtsp://localhost:8554/stream, which is the server currently running on JON. The stream will be accessible at this URL.
Running this command on the CLI of the JON will accomplish the task of sending the video stream to the local RTSP server. You can read more about the integration of Gstreramer with Jetson boards on the official documentation provided by NVIDIA .
The output of the command is shown in Figure 5.4.
Fig 5.4 RTSP Client Publisher
5.5 Configure RTSP Client Subscriber on Firecell 
This section will be divided in two parts: First  we analyze the command for testing the RTSP Client Subscriber, and the second we analyze its implementation in a python script, which is a fundamental step for performing object detection.

5.5.1 Testing
In order to check if the connection between the JON and the server is working, the first thing to do before implementing the Client in a python script is testing the connection via Gstreamer through the CLI of the Firecell. AFter installing Gstreamer package on our device we run this command:

gst-launch-1.0 rtspsrc \ location=rtsp://10.11.3.64:8554/stream latency=0 !\ decodebin ! autovideosink

A brief explanation of the command is as follows:
gst-launch-1.0: This is the GStreamer command-line tool used to build and run multimedia pipelines.
rtspsrc: This is a GStreamer element that retrieves video data from an RTSP source.
location=rtsp://10.11.3.64:8554/stream: This parameter specifies the location of the RTSP stream to be accessed. In this case, it's set to rtsp://10.11.3.64:8554/stream indicating the URL of the RTSP stream. Of course also in this case the used Ip is the static IP we set on the JON, but it must be changed based on the needs.
latency=0: This parameter sets the latency of the RTSP source. A latency of 0 indicates that the source should strive for minimal latency, which is desirable for real-time streaming applications.
decodebin: This is a GStreamer element that automatically detects and selects the appropriate decoder for the incoming video stream. It dynamically links to the appropriate decoder based on the stream's format and codecs. In our case it will automatically decode the stream in 10bit-h265, which is the format previously chosen for encoding.
autovideosink: This is a GStreamer element that automatically selects and initializes the appropriate video sink for displaying the video stream. It typically selects the default video sink for the current platform and environment.
Using this command we should be able to receive the video stream from the RTSP server running on the JON and displaying it on the default video sink of our system, as shown in Fig 5.5. 
5.5.2 Integration with Python
The next step concerns integrating the RTSP Client Subscriber in a python script. As explained in the next chapter, it is easier to use the video stream to perform the object detection if it is directly integrated in the same script. The script, his description and all the comments are available both at the github repository we created for this project , and in the Appendices.
This specific script for the implementation of the RTSP Client Subscriber with python is visible at Appendix 1 RTSPCLientSubscriber.py
The module that is necessary to install to make the program work is: OpenCV-Python, which is a Python library that interfaces with OpenCV, offering tools and algorithms for image processing and computer vision tasks, such as object detection and face recognition. It supports real-time video streaming, allowing developers to capture, process, and analyze video frames from cameras or video streams. This makes it ideal for applications like surveillance, live video analytics, and augmented reality, where real-time performance is crucial. Before running the program make sure you installed the library opencv executing: pip install opencv-python on the command line of your device . The integration of Gstreamer and OpenCV could may fail or cause problems, the most common ones and also the ones we encountered as explained in Chapter 5.7
Fig 5.5 RTSP Client Subscriber
5.6 Performing Object Detection with YOLOv8 

The very last step of our implementation of the project is about performing object detection on the video stream taken from the RTSP Client Subscriber. 
We decided to select PyCharm as the Integrated Development Environment (IDE) for this project; its alignment with the PyTorch framework underscores its suitability for facilitating machine learning workflows. While alternative IDEs such as Jupyter Notebook holds merit, PyCharm's native support for PyTorch significantly streamlines the development and management of machine learning scripts. As previously cited, the object detection’s task is executed through the YOLOv8 algorithm implemented in an extension of the python script mentioned in the last paragraph (RTSPCLientSubscriber.py). In order to integrate YOLOv8 in the python script it is necessary to install the ultralytics python module in our environment. It will be enough to just run the following command from the command line: pip install ultralytics, for more information consult the official documentation . The model we used to perform the object detection is yolov8m.pt, which is a pre-trained model on a very well-known and versatile dataset called “COCO”,  already available and usable when installing the ultralytics model, it is sufficient to implement the model in the script and the library will automatically fix the importation of the model.The script is so an extension of the previous one, it can be consulted both at the github repository we created and in Appendix 2, under the name main.py. The script is provided with all the comments and descriptions needed.
When the program is running, it will act as an RTSP Client, subscribing to the RTSP server available on the JON, and before showing the video, for each frame it performs object detection adding to the view bounding boxes and semantic class names to the spotted items. A demonstration of this is shown in Fig 5.6.


Fig 5.6 Python Script for Real-Time object detection


5.7 Bug Fixing Table 

In this paragraph we will analyze the most common errors that one can possibly face during the implementation of the system and how to fix them.

n.
Error
Fix
1
Camera not working with the testing command:
Camera not found
In this case the error could probably be that the setup of the pins of the JON is wrong. run this file: /opt/nvidia/jetson-io/jetson-io.py
and change the pins configuration of the cam slots on IMX477 dual
2
RTSP server not running
The mediaMTX server is normally ready to use, most-likely the error committed is that you have installed a version of the server which is not compatible with the architecture of the board. Make sure to check if your systems runs with an AMD or ARM processor and download the “linux” version of that one
3
Warning from the server: RTP packet loss
This Warning given by the RTSP server is very common. In order to solve it, access the file mediamtx.yml and change the line writeQueueSize increasing the value of the usable RAM memory. On the other hand if this is not enough because you can’t increase the RAM furthermore, try to decrease the quality or the framerate of the video stream 
4
Gstreamer doesn’t recognize pieces of the pipeline
In this case you should try to upgrade the version of Gstreamer, if you already have the last one available, try to install all the optional packages coming with Gstreamer, following this link: https://gstreamer.freedesktop.org/documentation/installing/index.html?gi-language=c


5
Firecell can’t receive the video stream from JON
In this case, the problem could be a networking issue, since in this phase we are working on the public network. check if the port forwarding (DNAT) is working properly using the ping command, and also if the firewalls running on the devices let RTP packets being received.
6
Gstreamer plug-in not working with OpenCV into python script
If the integration of Gstreamer with OpenCV is not working while running the python script, try to add this line at the beginning of the script, after importing cv2:
print(cv2.getBuildInformation())
at this point in the output you should see this line:
GStreamer: NO
To solve this problem and install the Gstreamer integration for OpenCV, follow this tutorial:
https://discuss.bluerobotics.com/t/opencv-python-with-gstreamer-backend/8842




