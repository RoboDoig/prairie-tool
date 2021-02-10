import sys

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, QObject

from interface import Interface
from ImageProviders import PyplotImageProvider, CvImageProvider
import matplotlib.pyplot as plt


if __name__ == '__main__':
    app = QApplication(sys.argv)

    appEngine = QQmlApplicationEngine()
    context = appEngine.rootContext()

    appEngine.load(QUrl('prairie-tool-qml/main.qml'))

    root = appEngine.rootObjects()[0]

    # Register python classes with qml
    interface = Interface(app, context, root, appEngine)
    context.setContextProperty('iface', interface)

    root.show()
    try:
        apcode = app.exec_()
    except:
        print('there was an issue')
    finally:
        sys.exit(apcode)
