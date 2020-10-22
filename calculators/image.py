#
# Data pipelines for Edge Computing
#
# Inspired by Google Media pipelines
#
#
# Dataflow can be within a "process" and then hook in locally
# But can also be via a "bus" or other communication mechanism
# 
#

# 
# Example: Draw detections
#
# Input 1. Picture
# Input 2. Detections [...]
#
# They can come in one single combined data-packet och as a picture that should be "annotated"
# with labels
#
import cvutils
import cv2
import mss
import numpy as np
from datetime import datetime
from calculators.core import Calculator
from yolo3.yolo3 import YoloV3


class ImageData:
    def __init__(self, image, timestamp):
        self.image = image
        self.timestamp = timestamp


class ImageMovementDetector(Calculator):
    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.avg = cvutils.DiffFilter()
        self.threshold = 0.01
        if options and 'threshold' in options:
            self.threshold = options['threshold']

    def process(self):
        image = self.get(0)
        print(image)
        if isinstance(image, ImageData):
            value = self.avg.calculate_diff(image.image)
            if value > self.threshold:
                print(" *** Trigger motion!!! => output set!")
                self.set_output(0, image)
                return True
        return False


class ShowImage(Calculator):
    def process(self):
        image = self.get(0)
        if isinstance(image, ImageData):
            cv2.imshow(self.name, image.image)
        return True

class ShowStatusImageFromFiles(Calculator):
    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.output_data = [None]
        if options is not None and 'onImage' in options:
            im_name = options['onImage']
            self.onImage = cv2.imread(im_name)
        if options is not None and 'offImage' in options:
            im_name = options['offImage']
            self.offImage = cv2.imread(im_name)
        self.onWord = "on"
        if options is not None and 'onWord' in options:
            self.onWord = options['onWord']

    def process(self):
        data = self.get(0)
        if data is not None:
            # Assuming string!
            print("Data:", data)
            if self.onWord in data:
                cv2.imshow("Status", self.onImage)
            else:
                cv2.imshow("Status", self.offImage)
        return True

class CaptureNode(Calculator):

    cap = None
    screens = None
    monitor_area = None

    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.output_data = [None]
        self.video = options['video'] if options and 'video' in options else 0
        if type(self.video) is str:
            if self.video.startswith('screen'):
                monitor = 1
                self.screens = mss.mss()
                # {'left': 0, 'top': -336, 'width': 6800, 'height': 1440}
                self.monitor_area = self.screens.monitors[monitor]
                print(f"*** Capture from {self.video} area {self.monitor_area}")
            elif self.video.startswith("rpicam"):
                cw, ch = 1280, 720
                dw, dh = 1280, 720
                fps = 60
                flip = 2
                self.video = ('nvarguscamerasrc ! '
                              'video/x-raw(memory:NVMM), width=%d, height=%d, format=NV12, framerate=%d/1 ! '
                              'nvvidconv flip-method=%d ! '
                              'video/x-raw, width=%d, height=%d, format=BGRx ! '
                              'videoconvert ! '
                              'video/x-raw, format=BGR ! appsink' %
                              (cw, ch, fps, flip, dw, dh)
                              )
            elif self.video.isnumeric():
                self.video = int(self.video)
        if not self.screens:
            print("*** Capture from", self.video)
            self.cap = cv2.VideoCapture(self.video)

    def process(self):
        if self.cap:
            _, frame = self.cap.read()
        elif self.screens:
            # Get raw pixels from the screen, save it to a Numpy array
            frame = np.array(self.screens.grab(self.monitor_area))
            frame = cv2.resize(frame, dsize=(self.monitor_area['width'] // 2, self.monitor_area['height'] // 2),
                               interpolation=cv2.INTER_CUBIC)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        else:
            return False
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        self.set_output(0, ImageData(frame, timestamp))
        return True

    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.screens:
            self.screens.close()
            self.screens = None


class YoloDetector(Calculator):
    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.input_data = [None]
        self.yolo = YoloV3(0.5, 0.4)

    def process(self):
        image = self.get(0)
        if isinstance(image, ImageData):
            nf = image.image.copy()
            d = self.yolo.detect(nf)
            if d != []:
                self.set_output(0, ImageData(nf, image.timestamp))
                self.set_output(1, d)
                return True
        return False


class DrawDetections(Calculator):
    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.input_data = [None, None]

    def process(self):
        if self.input_data[0] is not None and self.input_data[1] is not None:
            image = self.get(0)
            detections = self.get(1)
            if isinstance(image, ImageData):
                frame = image.image.copy()
                cvutils.drawDetections(frame, detections)
                self.set_output(0, ImageData(frame, image.timestamp))
                return True
        return False


class LuminanceCalculator(Calculator):
    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.input_data = [None]

    def process(self):
        if self.input_data[0] is not None:
            image = self.get(0)
            if isinstance(image, ImageData):
                gray = cv2.cvtColor(image.image, cv2.COLOR_BGR2GRAY)
                self.set_output(0, ImageData(gray, image.timestamp))
            return True


class SobelEdgesCalculator(Calculator):
    def __init__(self, name, s, options=None):
        super().__init__(name, s, options)
        self.input_data = [None]

    def process(self):
        if self.input_data[0] is not None:
            image = self.get(0)
            if isinstance(image, ImageData):
                img = cv2.GaussianBlur(image.image, (3,3), 0)
                sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
                self.set_output(0, ImageData(sobelx, image.timestamp))
            return True
