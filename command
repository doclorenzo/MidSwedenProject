lancia su rtsp camera
gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, framerate=30/1' ! nvvidconv ! rtspclientsink location=rtsp://localhost:8554/stream

solo camera
gst-launch-1.0 nvarguscamerasrc sensor_id=0 !    'video/x-raw(memory:NVMM),width=1920, height=1080, framerate=30/1' !    nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=540' !    nvvidconv ! nvegltransform ! nveglglessink -e


test
gst-launch-1.0 nvarguscamerasrc sensor_id=0 !    'video/x-raw(memory:NVMM),width=1920, height=1080, framerate=30/1' !    nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=540' !    nvvidconv !  rtspclientsink location=rtsp://localhost:8554/stream


gst-launch-1.0 nvarguscamerasrc sensor_id=0 !    'video/x-raw(memory:NVMM),width=1920, height=1080, framerate=30/1' !    nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=540' !    nvvidconv ! nvegltransform ! nveglglessink -e ! rtspclientsink location=rtsp://localhost:8554/stream


DEFINITIVo:
jeston:
gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=5/1' ! nvvidconv ! queue ! rtspclientsink location=rtsp://localhost:8554/stream 

server:
gst-launch-1.0 rtspsrc location=rtsp://10.11.3.64:8554/stream latency=0 ! decodebin ! autovideosink
