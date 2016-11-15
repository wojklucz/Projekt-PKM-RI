import cv2
import time
from trainCommunicator import TrainCommunicator

class CamCM():
    def __init__(self,filename):
        self.filename = filename

    def __enter__(self):
        self.camera = cv2.VideoCapture(self.filename)
        return self.camera

    def __exit__(self, *args):
        self.camera.release()



def findTrain():
    with CamCM("rtsp://admin:DoTestowania@172.20.16.105/profile2/media.smp") as camera:
        firstFrame = None
        begin = time.time()
        while True:
            (grabbed, frame) = camera.read()
            if not grabbed:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            if firstFrame is None:
                firstFrame = gray
                continue
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            lel = cv2.findNonZero(thresh)
            if lel is not None:
                if len(lel) > 200:
                    break
            if time.time() - begin > 5:
                print "Timeout"
                return -1,-1
        x = 0
        y = 0
        for element in lel:
            y += element[0][0]
            x += element[0][1]
        y = y / len(lel)
        x = x / len(lel)
    return x, y

tc = TrainCommunicator()
tc.connect()
train_coords = {}


for train in range(1,8):
    tc.set_speed_direction(train,40,0)
    x,y = findTrain()
    tc.set_speed_direction(train,0,0)
    if x > -1:
        train_coords[train] = x,y

print train_coords

# for train in range(7):
#     ret, frame = vcap.read()
#     tc.set_speed_direction(train,50,0)
#     sleep(2)
#     tc.set_speed_direction(train,0,0)
#     ret, frame2 = vcap.read()
#     frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#     frame = cv.GaussianBlur(frame, (21,21), 0)
#     frame2 = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
#     frame2 = cv.GaussianBlur(frame2, (21, 21), 0)
#     frameDelta = cv.absdiff(frame2, frame)
#     thresh = cv.threshold(frameDelta, 25, 255, cv.THRESH_BINARY)[1]
#     difflist.append(thresh)
#
# for idx,frame in enumerate(difflist):
#     cv.imwrite("diif" + str(idx) + ".jpg", frame)