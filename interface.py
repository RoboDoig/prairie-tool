from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QVariant, QTimer, QThread, QUrl, QSize, Qt
from PyQt5.QtGui import QImage
from PyQt5.QtQml import QQmlComponent
from PyQt5.QtQuick import QQuickItem, QQuickImageProvider
import time
import win32com.client
import numpy as np
import matplotlib.pyplot as plt
from ImageProviders import CvImageProvider, PyplotImageProvider, BasicImageProvider


class Interface(QObject):
    signal_start_job = pyqtSignal()

    def __init__(self, app, context, root, engine):
        QObject.__init__(self, root)
        self.app = app
        self.ctx = context
        self.root = root
        self.engine = engine

        # PrairieLink
        self.acquisition = Acquisition()

        # Image providers
        self.set_display()
        self.update_image_provider()
        self.get_img()

        # Thread worker
        self.worker = Worker(self.acquisition)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.signal_start_job.connect(self.worker.run)
        self.worker.on_image.connect(self.on_image)

    def get_img(self):
        self.live_image_provider.setImg(self.acquisition.get_mean_img())
        # self.live_image_provider.setImg(self.acquisition.last_frame)

        self.live_display.reload()
        self.ref_display.reload()
        self.analysis_display.reload()

    def set_display(self):
        self.live_display = self.root.findChild(QObject, "liveimage")
        self.ref_display = self.root.findChild(QObject, "refimage")
        self.analysis_display = self.root.findChild(QObject, "analysisimage")

    def update_image_provider(self):
        self.live_image_provider = BasicImageProvider(requestedImType='pixmap')
        self.engine.addImageProvider("liveimageprovider", self.live_image_provider)

        self.ref_image_provider = PyplotImageProvider(requestedImType='pixmap')
        self.engine.addImageProvider("refimageprovider", self.ref_image_provider)

        self.analysis_image_provider = PyplotImageProvider(requestedImType='pixmap')
        self.engine.addImageProvider("analysisimageprovider", self.analysis_image_provider)

    @pyqtSlot()
    def start_acquisition(self):
        self.acquisition.start_stream()
        self.signal_start_job.emit()

    @pyqtSlot()
    def stop_acquisition(self):
        self.worker.stop()
        self.worker.quit()
        self.worker.wait()
        self.acquisition.stop_stream()

    @pyqtSlot()
    def load_reference(self):
        self.get_img()

    @pyqtSlot()
    def on_image(self):
        self.get_img()


class Worker(QThread):
    on_image = pyqtSignal()

    def __init__(self, acquisiton):
        super(Worker, self).__init__()
        self.isRunning = False
        self.acquisition = acquisiton

    @pyqtSlot()
    def run(self):
        if not self.isRunning:
            self.isRunning = True

        while self.isRunning:
            self.acquisition.frame_stream()
            self.on_image.emit()

    @pyqtSlot()
    def stop(self):
        self.isRunning = False


class Acquisition:
    def __init__(self):
        self.pl = win32com.client.Dispatch("PrairieLink64.Application")

        # TODO - this stuff should probs happen in the start stream, disconnection in stop stream
        print('Connected to PrairieLink: ', self.pl.Connect())

        self.pl.SendScriptCommands('-DoNotWaitForScans')
        self.pl.SendScriptCommands('-LimitGSDMABufferSize true 100')
        self.pl.SendScriptCommands('-StreamRawData true 0')
        self.pl.SendScriptCommands('-fa 1')  # set frame averaging to 1

        # Get acquisition settings
        self.samplesPerPixel = self.pl.SamplesPerPixel()
        self.pixelsPerLine = self.pl.PixelsPerLine()
        self.linesPerFrame = self.pl.LinesPerFrame()
        self.totalSamplesPerFrame = self.samplesPerPixel * self.pixelsPerLine * self.linesPerFrame

        # flush buffer
        self.flush_buffer()

        self.last_frame = None
        self.running_average = 16
        self.frame_buffer = np.zeros((self.running_average, self.linesPerFrame, self.pixelsPerLine))

        # for debugging
        # print('Disconnected from PrairieLink: ', self.pl.Disconnect())

    def flush_buffer(self):
        flushing = True
        while flushing:
            samples, numSamplesRead = self.pl.ReadRawDataStream(0)
            print(numSamplesRead, 'samples read')
            if numSamplesRead == 0:
                flushing = False

    def start_stream(self):
        self.buffer = []

        self.flush_buffer()
        self.pl.SendScriptCommands('-lv on')

    def stop_stream(self):
        self.pl.SendScriptCommands('-lv off')
        self.flush_buffer()

    def get_mean_img(self):
        return np.mean(self.frame_buffer, axis=0)

    def frame_stream(self):
        # get raw data stream
        samples, numSamplesRead = self.pl.ReadRawDataStream(0)

        # append to old data
        self.buffer = np.append(self.buffer, samples[0:numSamplesRead])

        # extract full frames
        numWholeFramesGrabbed = np.floor(len(self.buffer)/self.totalSamplesPerFrame)
        toProcess = self.buffer[0:int(numWholeFramesGrabbed*self.totalSamplesPerFrame)]

        # clear data from buffer
        self.buffer = self.buffer[int(numWholeFramesGrabbed*self.totalSamplesPerFrame)::]

        # process acquired frames - just get the last full frame
        if numWholeFramesGrabbed > 0:
            frame = toProcess[0:self.totalSamplesPerFrame]

            # save the last frame captured
            self.last_frame = self.process_frame(frame)

            # roll frame buffer back and add last frame
            self.frame_buffer = np.roll(self.frame_buffer, -1, 0)
            self.frame_buffer[-1] = self.last_frame
            # print(np.mean(np.mean(self.frame_buffer, axis=1), axis=1))

    def process_frame(self, in_frame):
        out_frame = np.zeros(self.linesPerFrame * self.pixelsPerLine)
        do_flip = True
        # row loop
        for i in range(self.linesPerFrame):
            do_flip = not do_flip

            # column loop
            for j in range(self.pixelsPerLine):

                # sample loop
                pixel_sum = 0
                pixel_count = 0

                for k in range(self.samplesPerPixel):
                    sample_value = in_frame[(i*self.linesPerFrame*self.samplesPerPixel) + (j*self.samplesPerPixel) + k]
                    # sampleValue -= 8192 (???)
                    if sample_value >= 0:
                        pixel_sum += sample_value
                        pixel_count += 1

                if do_flip:
                    index = (i*self.linesPerFrame) + (self.pixelsPerLine - 1 - j)
                else:
                    index = (i*self.linesPerFrame) + j
                out_frame[index] = pixel_sum / pixel_count

        out_frame = out_frame.reshape((self.linesPerFrame, self.pixelsPerLine))
        return out_frame



