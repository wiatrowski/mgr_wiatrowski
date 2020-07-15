# import system modules
import sys
import threading

# import some PyQt5 modules
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication , QMainWindow

# import users modules
from centroidTracker import CentroidTracker

# import other module
import cv2
import numpy as np
import time


class MainWindow(QMainWindow):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super(MainWindow, self).__init__()
        loadUi('mainWindow.ui', self)
        self.flagControlCamera = False

        self.leftPolygon = []
        self.leftCountedProducts = 0
        self.rightPolygon = []
        self.rightCountedProducts = 0
        self.lowValColors = []
        self.highValColors = []

        self.thread_1 = threading.Thread(target=self.viewCam)

        self.control_bt.clicked.connect(self.controlCamera)
        self.buttonUndoPoint.clicked.connect(self.undoPoint)
        self.buttonDeletePoints.clicked.connect(self.deletePoints)
        self.buttonSavePoints.clicked.connect(self.savePoints)

    def nothing(self):
        pass

    # view camera
    def viewCam(self):

        ct = CentroidTracker(maxDisappeared=10, maxDistance=150)

        video = cv2.VideoCapture(0)
        numberCountedProducts = 0
        #const functions

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        # get image infos
        height, width, channel = 480, 640, 3 # image.shape
        step = 1920 # channel * width
        # do usubiea

        self.rightPolygon = [[361, 134], [602, 133], [603, 318], [371, 320]]

        while True:

            #start = time.clock()
            _, frame = video.read()

            # Blur methods available, comment or uncomment to try different blur methods.
            imgBlur = cv2.GaussianBlur(frame, (7, 7), 1)



            # HSV (Hue, Saturation, Value).
            hsv = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2HSV)

            # HSV values to define a colour range.
            self.lowValColors = np.array([self.sliderLHue.value(), self.sliderLSat.value(), self.sliderLVal.value()])
            self.highValColors = np.array([self.sliderHHue.value(), self.sliderHSat.value(), self.sliderHVal.value()])

            # First mask.
            mask = cv2.inRange(hsv, self.lowValColors, self.highValColors)

            # Mask with Morph
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            rects = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.sliderLArea.value() and area < self.sliderHArea.value():
                    cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                    x, y, w, h, = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=2)
                    box = np.array([x, y, x + w, y + h])
                    rects.append(box.astype("int"))
                    #print(area)

            objects = ct.update(rects)

            if self.rightPolygon: cv2.polylines(frame, [np.array(self.rightPolygon)], isClosed=True, color=(0, 255, 0), thickness=2)
            if self.leftPolygon: cv2.polylines(frame, [np.array(self.leftPolygon)], isClosed=True, color=(255, 0, 0), thickness=2)

            for (objectID, centroid) in objects.items():
                centroidX, centroidY = centroid
                # draw both the ID of the object and the centroid of the
                # object on the output frame
                cv2.putText(frame, "ID {}".format(objectID), (centroidX, centroidY),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                cv2.circle(frame, (centroidX, centroidY), 4, (255, 0, 0), -1)

                if self.leftPolygon:
                    polygonTest = cv2.pointPolygonTest(np.array(self.leftPolygon), (centroidX, centroidY), False)
                    if polygonTest == 1 and ct.countingStatus(objectID) is True:
                        self.leftCountedProducts += 1
                        self.lcdNumberLeft.display(self.leftCountedProducts)
                if self.rightPolygon:
                    polygonTest = cv2.pointPolygonTest(np.array(self.rightPolygon), (centroidX, centroidY), False)
                    if polygonTest == 1 and ct.countingStatus(objectID) is True:
                        self.rightCountedProducts += 1
                        self.lcdNumberRight.display(self.rightCountedProducts)
                #polygonTest = cv2.pointPolygonTest(np.array(self.rightPolygon), (centroidX, centroidY), False)
                #if polygonTest == 1 and ct.countingStatus(objectID) is True:
                #    self.rightCountedProducts += 1
                #    self.lcdNumberRight.display(self.rightCountedProducts)

            if self.leftCountedProducts == self.boxCountNumber.value():
                print('tu funkcja zmieniajaca i resetujaca')
                self.leftCountedProducts = 0
            if self.rightCountedProducts == self.boxCountNumber.value():
                print('tu funkcja zmieniajaca i resetujaca')
                self.rightCountedProducts = 0

            # convert image to RGB format
            if self.radioFrame.isChecked():
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.radioMask.isChecked():
                # Put mask over top of the original image.
                result = cv2.bitwise_and(frame, frame, mask=mask)
                image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

            # create QImage from image
            qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
            # show image in img_label
            self.image_label.setPixmap(QPixmap.fromImage(qImg))

            #elapsed = time.clock()
            #elapsed = elapsed - start
            #print("Time spent in (function name) is: ", elapsed)
            

    def controlCamera(self):
        if self.flagControlCamera is False:
            self.thread_1.start()
            self.flagControlCamera = not self.flagControlCamera
        else:
            print(' ')

    def mouseDoubleClickEvent(self, point):
        x, y = point.x(), point.y()
        if self.radioLPolygon.isChecked():
            self.leftPolygon.append([x, y])
        elif self.radioRPolygon.isChecked():
            self.rightPolygon.append([x, y])

    def undoPoint(self):
        if self.radioLPolygon.isChecked() and self.leftPolygon:
            self.leftPolygon.pop()
        elif self.radioRPolygon.isChecked() and  self.rightPolygon:
            self.rightPolygon.pop()

    def deletePoints(self):
        if self.radioLPolygon.isChecked() and self.leftPolygon:
            self.leftPolygon = []
        elif self.radioRPolygon.isChecked() and  self.rightPolygon:
            self.rightPolygon = []

    def savePoints(self):
        print('jo, zapisuje')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())