import cv2 as cv
import numpy as np
import serial
import time

ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)


cap = cv.VideoCapture(0)

motion_detected = False

while cap.isOpened():
    ret,frame1 = cap.read()
    ret,frame2 = cap.read()

    motionDiff = cv.absdiff(frame1, frame2)
    motionGray = cv.cvtColor(motionDiff, cv.COLOR_BGR2GRAY)
    
    motionBlur = cv.GaussianBlur(motionGray, (7,7), 0)

    _, thres = cv.threshold(motionBlur, 25, 255, cv.THRESH_BINARY)
    motionDilate = cv.dilate(thres, None, iterations=6)
    motionDilate = cv.morphologyEx(motionDilate, cv.MORPH_CLOSE, np.ones((15, 15), np.uint8))

    motionContours, _ = cv.findContours(motionDilate, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    current_motion = False

    for findContours in motionContours:
        if (cv.contourArea(findContours) > 5000):

            x,y,w,h = cv.boundingRect(findContours)
            ser.write(f"{int(x)},{int(y)}\n".encode())
            cv.rectangle(frame1, (x,y), (x+w, y+h), (0,255,0), 2)
            current_motion = True


    if current_motion and not motion_detected:
        ser.write(b'motion_detected\n')
        motion_detected = True
    elif not current_motion and motion_detected:
        ser.write(b'motion_cleared\n')
        motion_detected = False



    cv.imshow("Security Camera", frame1)
    frame1 = frame2
    ret,frame2 = cap.read()

    if (cv.waitKey(1) & 0XFF == ord("q")):
        break

cap.release()
cv.destroyAllWindows()

