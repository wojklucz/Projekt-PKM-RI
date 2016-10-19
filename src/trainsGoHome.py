import cv2 as cv

vcap = cv.VideoCapture("rtsp://admin:DoTestowania@172.20.16.105/profile1/media.smp")

while(1):
    ret, frame = vcap.read()
    cv.imshow('VIDEO', frame)
    cv.waitKey(1)