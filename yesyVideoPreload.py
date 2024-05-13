from ultralytics import YOLO
import cv2
import math

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

# Load a pretrained YOLO model
model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER) #enables the camera

#sets resolutuion


while True:
    ret, img= cap.read()  #reads the image
    results = model(img, stream=True) #before showing it, it "gives the image to Yolo" to detect obejcts in the array results



    for r in results:  #iterate trhought the found boxes
        boxes = r.boxes

        for box in boxes: #takes the box
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0] #takes the coordinates
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values the coord.

            # put box in cam
            # create rectangle function arguments: image / coordinated start, end / color of rectangle / thickness
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # confidence
            confidence = math.ceil((box.conf[0]*100))/100  #caluatethe accuracy
            print("Confidence --->",confidence)
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2
            text=r.names[box.cls[0].item()]  #name of class of object
            text+= f" {confidence}"  #adds the conficende to the type of object string took before

            cv2.putText(img, text , org, font, fontScale, color, thickness)  #creste the text to show

    cv2.imshow('Webcam', img) #create the window with video stream, rectangle and text created before


    if cv2.waitKey(1) == ord('q'):  #quit pressing 'q'
        break

cap.release()
cv2.destroyAllWindows()