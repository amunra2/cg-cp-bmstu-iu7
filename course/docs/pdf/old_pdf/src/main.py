# This Python file uses the following encoding: utf-8
import sys
import os

from PyQt5 import QtWidgets, uic
# from darktheme.widget_template import DarkPalette

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QMessageBox, QColorDialog
from PyQt5.QtGui import QColor
from ui_mainwindow import Ui_project

from wingl import setHeightWF, setParticleSize, winGL

BACKGROUNDSTRING = "background-color: %s"



class project(QtWidgets.QMainWindow, Ui_project):
    def __init__(self, *args, **kwargs):
        super(project, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.curColor = QColor(0, 0, 255, 1)
        self.colorWindow = None
        
        self.isActiveWF = True

        self.translateVec = {"w": False, "s" : False, "a": False, "d": False}

        # Взаимодействие с окном
        
        # Камера
        # Перемещение
        self.cam_move_up_btn.clicked.connect(self.moveUp)
        self.cam_move_down_btn.clicked.connect(self.moveDown)
        self.cam_move_left_btn.clicked.connect(self.moveLeft)
        self.cam_move_right_btn.clicked.connect(self.moveRight)
        self.cam_move_forward_btn.clicked.connect(self.moveForward)
        self.cam_move_back_btn.clicked.connect(self.moveBack)

        # Поворот
        self.cam_spin_up_btn.clicked.connect(self.spinLeftY)
        self.cam_spin_down_btn.clicked.connect(self.spinRightY)
        self.cam_spin_left_btn.clicked.connect(self.spinLeftX)
        self.cam_spin_right_btn.clicked.connect(self.spinRightX)

        # Масштабирование
        self.cam_scale_forward_btn.clicked.connect(self.scaleUp)
        self.cam_sclale_back_btn.clicked.connect(self.scaleDown)

        # Водопад
        self.wf_run_btn.clicked.connect(self.controllWaterfall)
        # self.speed_up_wf_btn.clicked.connect(self.changeSpeedUpWF)
        # self.speed_down_wf_btn.clicked.connect(self.changeSpeedDownWF)
        self.sliderSpeedWF.valueChanged.connect(self.changeSpeedWF)
        self.sliderHeightWF.valueChanged.connect(self.changeHeightWF)
        self.sliderAngleWF.valueChanged.connect(self.changeAngleWF)
        self.sliderSizeParticle.valueChanged.connect(self.changeParticleSize)
        self.sliderAmountParticles.valueChanged.connect(self.changeParticlesAmount)

        # Таймер
        timer = QtCore.QTimer(self)
        timer.setInterval(1)
        timer.timeout.connect(self.timerActions)
        timer.start()

        timerW = QtCore.QTimer(self)
        timerW.setInterval(300)
        timerW.timeout.connect(self.timerUpdateWaterColor)
        timerW.start()


    def timerActions(self):
        if self.colorWindow:
            self.curColor = self.colorWindow.currentColor()
            self.colorBtn.setStyleSheet(
                BACKGROUNDSTRING % self.curColor.name()
            )
        
        if (self.isActiveWF):
            self.winGL.makeWaterfall()
        
        self.winGL.update(self.curColor.getRgbF(), self.translateVec)
        self.setWindowTitle("FPS: %5s (частиц: %5s)" %(self.winGL.getFPS(), self.winGL.getAmountParticles()))


    def timerUpdateWaterColor(self):
        self.winGL.updateWaterColor()


    # Управление водопадом
    def controllWaterfall(self):
        self.isActiveWF = not self.isActiveWF


    def changeSpeedWF(self, value):
        self.winGL.changeSpeedWF(value)


    def changeAngleWF(self, value):
        self.winGL.changeAngleWF(value)


    def changeParticleSize(self, value):
        setParticleSize(value)


    def changeParticlesAmount(self, value):
        self.winGL.changeParticlesAmount(value)


    def changeHeightWF(self, value):
        setHeightWF(value)
        self.winGL.changeHeightAliveWF(value)
        self.winGL.changeHeightRock(value)

    # Масштабирование
    def scaleUp(self):
        self.winGL.scale(1)

    def scaleDown(self):
        self.winGL.scale(-1)

    # Перемещение
    def moveUp(self):
        self.winGL.translate((0, 1, 0))

    def moveDown(self):
        self.winGL.translate((0, -1, 0))

    def moveLeft(self):
        self.winGL.translate((1, 0, 0))

    def moveRight(self):
        self.winGL.translate((-1, 0, 0))

    def moveForward(self):
        self.winGL.translate((0, 0, -1))

    def moveBack(self):
        self.winGL.translate((0, 0, 1))

    # Поворот
    def spinLeftX(self):
        self.winGL.spin((0, -1, 0))

    def spinRightX(self):
        self.winGL.spin((0, 1, 0))

    def spinLeftY(self):
        self.winGL.spin((1, 0, 0))

    def spinRightY(self):
        self.winGL.spin((-1, 0, 0))

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_W):
            self.translateVec["w"] = True
        elif (event.key() == Qt.Key_S):
            self.translateVec["s"] = True
        elif (event.key() == Qt.Key_A):
            self.translateVec["a"] = True
        elif (event.key() == Qt.Key_D):
            self.translateVec["d"] = True

    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key_W):
            self.translateVec["w"] = False
        elif (event.key() == Qt.Key_S):
            self.translateVec["s"] = False
        elif (event.key() == Qt.Key_A):
            self.translateVec["a"] = False
        elif (event.key() == Qt.Key_D):
            self.translateVec["d"] = False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = project()
    widget.show()
    sys.exit(app.exec_())
