import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.13
import QtQuick.Shapes 1.11

ApplicationWindow {
    id: root
    width: 1020
    height: 640
    visible: true
    title: qsTr("prairie-tool")



    Rectangle {
        id: rectangle
        color: "#c1c1c1"
        anchors.fill: parent
    }

    GridLayout {
        id: imageLayout
        anchors.fill: parent
        anchors.topMargin: 82
        rows: 1
        columns: 3

        Image {
            id: liveImage
            width: 100
            height: 100
            objectName: "liveimage"
            fillMode: Image.PreserveAspectFit
            source: "image://liveimageprovider/img"
            Layout.fillHeight: true
            Layout.fillWidth: true
            cache: false
            function reload() {
                var oldSource = source;
                source = "";
                source = oldSource;
            }
        }

        Image {
            id: referenceImage
            width: 167
            height: 153
            objectName: "refimage"
            source: "image://refimageprovider/img"
            Layout.fillHeight: true
            Layout.fillWidth: true
            cache: false
            fillMode: Image.PreserveAspectFit
            function reload() {
                var oldSource = source;
                source = "";
                source = oldSource;
            }
        }

        Image {
            id: resultsImage
            objectName: "analysisimage"
            width: 100
            height: 100
            source: "image://analysisimageprovider/img"
            cache: false
            Layout.fillHeight: true
            Layout.fillWidth: true
            fillMode: Image.PreserveAspectFit
            function reload() {
                var oldSource = source;
                source = "";
                source = oldSource;
            }
        }

    }

    GridLayout {
        id: controlsLayout
        y: 0
        height: 83
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        rows: 1
        columns: 3

        Button {
            id: startAcquisitionButton
            text: qsTr("Start Acquisition")
            font.family: "Courier"
            font.pointSize: 13
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            onClicked: {
                iface.start_acquisition()
            }
        }


        Button {
            id: stopAcquisitionButton
            text: qsTr("Stop Acquisition")
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            font.family: "Courier"
            font.pointSize: 13
            onClicked: {
                iface.stop_acquisition()
            }
        }
        Button {
            id: loadReferenceImageButton
            text: qsTr("Load Reference")
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            font.pointSize: 13
            font.family: "Courier"
            onClicked: {
                iface.load_reference()
            }
        }
    }


}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.66}D{i:6}
}
##^##*/
