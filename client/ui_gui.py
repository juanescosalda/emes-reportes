# Form implementation generated from reading ui file 'c:\Users\juane\Desktop\Emes reportes\client\gui.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(948, 618)
        Dialog.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 255);\n"
"\n"
"")
        self.advanceFile = QtWidgets.QLineEdit(Dialog)
        self.advanceFile.setGeometry(QtCore.QRect(160, 60, 620, 31))
        self.advanceFile.setStyleSheet("")
        self.advanceFile.setObjectName("advanceFile")
        self.suppliersFile = QtWidgets.QLineEdit(Dialog)
        self.suppliersFile.setGeometry(QtCore.QRect(160, 200, 620, 30))
        self.suppliersFile.setObjectName("suppliersFile")
        self.toFile = QtWidgets.QLineEdit(Dialog)
        self.toFile.setGeometry(QtCore.QRect(160, 340, 620, 30))
        self.toFile.setObjectName("toFile")
        self.advancePath = QtWidgets.QPushButton(Dialog)
        self.advancePath.setGeometry(QtCore.QRect(800, 60, 90, 30))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        self.advancePath.setFont(font)
        self.advancePath.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.advancePath.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:15px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}\n"
"")
        self.advancePath.setObjectName("advancePath")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 60, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"color: rgb(0, 150, 214);\n"
"")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(50, 200, 111, 31))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"color: rgb(0, 150, 214);\n"
"")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(50, 340, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"color: rgb(0, 150, 214);\n"
"")
        self.label_3.setObjectName("label_3")
        self.uploadButton = QtWidgets.QPushButton(Dialog)
        self.uploadButton.setGeometry(QtCore.QRect(50, 520, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.uploadButton.setFont(font)
        self.uploadButton.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.uploadButton.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:20px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}\n"
"\n"
"")
        self.uploadButton.setCheckable(False)
        self.uploadButton.setChecked(False)
        self.uploadButton.setObjectName("uploadButton")
        self.runButton = QtWidgets.QPushButton(Dialog)
        self.runButton.setGeometry(QtCore.QRect(475, 520, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.runButton.setFont(font)
        self.runButton.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.runButton.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:20px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}")
        self.runButton.setObjectName("runButton")
        self.useButton = QtWidgets.QPushButton(Dialog)
        self.useButton.setGeometry(QtCore.QRect(685, 520, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.useButton.setFont(font)
        self.useButton.setMouseTracking(False)
        self.useButton.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.useButton.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:20px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}")
        self.useButton.setObjectName("useButton")
        self.suppliersPath = QtWidgets.QPushButton(Dialog)
        self.suppliersPath.setGeometry(QtCore.QRect(800, 200, 90, 30))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        self.suppliersPath.setFont(font)
        self.suppliersPath.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:15px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}")
        self.suppliersPath.setObjectName("suppliersPath")
        self.toPath = QtWidgets.QPushButton(Dialog)
        self.toPath.setGeometry(QtCore.QRect(800, 340, 90, 30))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        self.toPath.setFont(font)
        self.toPath.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:15px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}")
        self.toPath.setObjectName("toPath")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(0, 0, 951, 611))
        self.label_5.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 255, 255,255);\n"
"border-image: url(:/cct/logo_emes.png);")
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.chooseSuppliersButton = QtWidgets.QPushButton(Dialog)
        self.chooseSuppliersButton.setGeometry(QtCore.QRect(265, 520, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Sans Serif Collection")
        font.setPointSize(9)
        self.chooseSuppliersButton.setFont(font)
        self.chooseSuppliersButton.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.chooseSuppliersButton.setStyleSheet("QPushButton {\n"
"    background-color: rgb(0, 150, 214);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width:2px;\n"
"    border-radius:20px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(141, 206, 233);\n"
"}")
        self.chooseSuppliersButton.setObjectName("chooseSuppliersButton")
        self.label_5.raise_()
        self.advanceFile.raise_()
        self.suppliersFile.raise_()
        self.toFile.raise_()
        self.advancePath.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.uploadButton.raise_()
        self.runButton.raise_()
        self.useButton.raise_()
        self.suppliersPath.raise_()
        self.toPath.raise_()
        self.chooseSuppliersButton.raise_()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Reportes Emes"))
        self.advancePath.setText(_translate("Dialog", "Cargar"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:500;\">Reporte 260</span></p></body></html>"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:500;\">Proveedores</span></p></body></html>"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:500;\">Guardar en</span></p></body></html>"))
        self.uploadButton.setText(_translate("Dialog", "Cargar archivos"))
        self.runButton.setText(_translate("Dialog", "Comparar descuentos"))
        self.useButton.setText(_translate("Dialog", "Incluir aprovechamiento"))
        self.suppliersPath.setText(_translate("Dialog", "Cargar"))
        self.toPath.setText(_translate("Dialog", "Buscar"))
        self.chooseSuppliersButton.setText(_translate("Dialog", "Seleccionar proveedores"))
