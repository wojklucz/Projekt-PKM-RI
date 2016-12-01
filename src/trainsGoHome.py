import cv2
import time
import random
from trainCommunicator import TrainCommunicator
from time import sleep
import numpy as np
import strefyWycinekOperacyjny

class CamCM():
    def __init__(self,filename):
        self.filename = filename

    def __enter__(self):
        self.camera = cv2.VideoCapture(self.filename)
        return self.camera

    def __exit__(self, *args):
        self.camera.release()

def get_zone(arg):
    print arg
    return random.randint(1,10)

def find_train(whichCam):
    with CamCM(whichCam) as camera:
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
            if time.time() - begin > 3:
                return -1,-1
        x = 0
        y = 0
        for element in lel:
            y += element[0][0]
            x += element[0][1]
        y = y / len(lel)
        x = x / len(lel)
    return x, y


# #inicjalizacja
# tc = TrainCommunicator()
# tc.connect()
# train_coords1 = {}
# train_coords2 = {}
# trainz_not_found = list(range(1,7))
#
#
# #pomiar z pierwszej kamery
# for train in trainz_not_found:
#     tc.set_speed_direction(train,40,0)
#     x,y = find_train("rtsp://admin:DoTestowania@172.20.16.105/profile2/media.smp")
#     if (x,y) == (-1,-1):
#         print str(train) + ": not found."
#     tc.set_speed_direction(train,0,0)
#     sleep(1) # wait until stops
#     if x > -1:
#         train_coords1[train] = x,y
#         trainz_not_found.remove(train)
#
#
# #pomiar z drugiej kamery
# for train in trainz_not_found:
#     tc.set_speed_direction(train,40,1)
#     x,y = find_train("rtsp://admin:DoTestowania@172.20.16.106/profile2/media.smp")
#     if (x,y) == (-1,-1):
#         print str(train) + ": not found."
#     tc.set_speed_direction(train,0,0)
#     sleep(1)  # wait until stops
#     if x > -1:
#         train_coords2[train] = x,y
#         trainz_not_found.remove(train)
#
# #nie mamy funkcji mapujacej wspolrzedne z kamer na strefy, zatem wybieramy losowa strefe spod kamery i wyznaczamy trase
# #wrzucamy je do dicta
# train_coords = train_coords1.copy()
# train_coords.update(train_coords2)
#
# print train_coords
# train_zone_mapping = {}
# for key in train_coords:
#     train_zone_mapping[key] = get_zone(train_coords[key])
#
# print train_zone_mapping
droga = strefyWycinekOperacyjny.bfs(21,23)
print droga

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