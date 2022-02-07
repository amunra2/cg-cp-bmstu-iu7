from operator import imod
from PyQt5 import QtGui, QtOpenGL
from PyQt5.QtGui import QMatrix4x4, QCursor, QColor
from PyQt5.QtCore import Qt, QPoint

import OpenGL.GL as gl
from OpenGL import GLU
from OpenGL.arrays import vbo

import glm
import glfw
import numpy as np
from random import random

from shader import Shader

from object import Object
from camera import Camera

from particle import Particle



class winGL(QtOpenGL.QGLWidget):
    newParticlesMean = 50.0
    newParticlesVariance = 5.0

    active = True

    maxAge = 70

    def __init__(self, parent = None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.camMode = False
        # self.setMouseTracking(self.camMode)
        self.cursor = QCursor()

        self.color = (255, 255, 255, 1.0)
        self.angle = 0
        
        self.object = Object()
        self.camera = Camera()

        self.particlesNum = 1000

        self.particles = self.createParticles()
        self.particlesPositions = self.getParticlesPositions()
        self.particlesColors = self.getParticlesColor()

        # print("POS: ", type(self.particlesPositions[0]))

        # Модель, выводимая на экран
        self.vrtxs1 = np.array(
        (
         (-2, -0.5, 0),
         ( 3, -0.5, 0),
         ( 0,  0.5, 0),
         (-1,  0.5, 0)
        ),
        dtype='float32')

        print("VRTXS1: ", type(self.vrtxs1[0]))

        # self.vrtxs2 = np.array(
        # ((-0.5, -0.5, 0),
        #  ( 0.5, -0.5, 0),
        #  ( 0.5,  0.5, 0),
        #  (-0.5,  0.5, 0)
        # ),
        # dtype='float32')

        self.indices = np.array([i for i in range(self.particlesNum * 80)], dtype='int32')


    def createParticles(self):

        particles = []

        for i in range(self.particlesNum):
            particles.append(Particle())

        return particles


    def initializeGL(self):
        print("START Init")
        self.qglClearColor(QtGui.QColor(50, 50, 50))
        gl.glEnable(gl.GL_DEPTH_TEST)


    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.camera.changePerspective(ratio = width / height)
        self.camera.setPos([-20, 0, 0])
        self.camera.spinY(90)


    def paintGL(self):
        # print("Paint START")

        # Очищаем экран
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Создание объекта вершинного массива
        VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(VAO)

        # Установка шейдеров
        shaders = Shader("shader.vs", "shader.fs")
        shaders.use()

        # Преобразование
        shaders.setMat4("perspective", self.camera.getProjMatrix())
        shaders.setMat4("view", self.camera.getViewMatrix())
        shaders.setMat4("model", self.object.getModelMatrix())

        # Копирование массива вершин в вершинный буфер
        VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.particlesPositions, gl.GL_STATIC_DRAW)

        colorVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, colorVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.particlesColors, gl.GL_STATIC_DRAW)

        # Установка указателей вершинных атрибутов
        # posss = gl.glGetAttribLocation(shaders, "position")
        gl.glEnableVertexAttribArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)

        gl.glEnableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, colorVBO)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, True, 0, None)


        # Установка цвета
        # shaders.setVec4("curColor", *self.color)

        # Отрисовка
        # gl.glBindVertexArray(VAO)

        gl.glVertexAttribDivisor(0, 0)
        gl.glVertexAttribDivisor(1, 1)

        gl.glPointSize(5)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self.particles))

        
    
    def getParticlesColor(self):
        colors = []

        for particle in self.particles:
            colors.append(glm.vec4(0, 0, 1, 1))

        npColors = np.array(colors)
        

        return npColors

    def getParticlesPositions(self):
        positions = []

        for particle in self.particles:
            positions.append(particle.getPosition())

        poses = np.array(positions)

        return poses


    def moveParticles(self):

        movedParticles = []
        
        for particle in self.particles:
            particle.moveParticle()

        self.particlesPositions = self.getParticlesPositions()
        

    def makeWaterfall(self):
        print("Particles: ", len(self.particles))
        deletedParticles = 0

        # Удалить упавшие капли
        for particle in self.particles:
            if (particle.age > particle.maxAge):
                self.particles.pop(0)
                # self.particles.append(Particle())
                deletedParticles += 1

        self.particlesNum -= deletedParticles

        # Добавить еще частиц
        extraParticlesNum = int(self.newParticlesMean + random() * self.newParticlesVariance)

        for i in range(extraParticlesNum):
            self.particles.append(Particle())

        self.particlesNum += extraParticlesNum

        # Обновить атрибуты для всех частиц
        self.moveParticles()
    
    def translate(self, vec):
        self.camera.translate(*vec)

    def scale(self, k):
        self.camera.zoom(k)

    def spin(self, vec):
        self.camera.spinX(vec[0])
        self.camera.spinY(vec[1])
        self.camera.spinZ(vec[2])

    # Мышка
    def mousePressEvent(self, event):
        camPosition = self.pos()

        self.lastPos = QPoint(camPosition.x() + self.width() // 2,
                              camPosition.y() + self.height() // 2)

        self.cursor.setPos(self.lastPos)
        self.cursor.setShape(Qt.BlankCursor)

        if (event.button() == Qt.LeftButton):
            self.camMode = not self.camMode
            self.setMouseTracking(self.camMode)
        
        if (self.camMode):
            print("Dynamic CAM: On")
        else:
            print("Dynamic CAM: Off")


    def mouseMoveEvent(self, event):
        curPos = event.globalPos()

        if (self.lastPos == curPos):
            return

        deltaX = curPos.x() - self.lastPos.x()
        deltaY = self.lastPos.y() - curPos.y()
        self.lastPos = curPos

        self.camera.rotation(deltaX, deltaY)

    
    def wheelEvent(self, event):
        zoomK = event.pixelDelta().y() / 100
        self.camera.zoom(zoomK)


    def update(self, color, translateVec):
        self.camera.continousTranslate(translateVec)
        self.color = color
        self.updateGL()



# Старый отрисовщик


    # def paintGL(self):
    #     # print("Paint START")

    #     # Очищаем экран
    #     gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        

    #     # Создание объекта вершинного массива
    #     VAO = gl.glGenVertexArrays(1)
    #     gl.glBindVertexArray(VAO)

    #     # Копирование массива вершин в вершинный буфер
    #     VBO = gl.glGenBuffers(1)
    #     gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    #     gl.glBufferData(gl.GL_ARRAY_BUFFER, self.particlesPositions, gl.GL_STATIC_DRAW)

    #     # Копирование индексного массива в элементный буфер
    #     EBO = gl.glGenBuffers(1)
    #     gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
    #     gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices, gl.GL_STATIC_DRAW)

    #     # Установка указателей вершинных атрибутов
    #     gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
    #     gl.glEnableVertexAttribArray(0)

    #     # Установка шейдеров
    #     shaders = Shader("shader.vs", "shader.fs")
    #     shaders.use()

    #     # Преобразование
    #     shaders.setMat4("perspective", self.camera.getProjMatrix())
    #     shaders.setMat4("view", self.camera.getViewMatrix())
    #     shaders.setMat4("model", self.object.getModelMatrix())

    #     # Установка цвета
    #     shaders.setVec4("curColor", *self.color)

    #     # Отрисовка
    #     gl.glBindVertexArray(VAO)
    #     gl.glPointSize(5)
    #     gl.glDrawElements(gl.GL_POINTS, self.particlesNum * 100, gl.GL_UNSIGNED_INT, None)

    #     # gl.glDrawArrays

    #     # self.particles = self.createParticles()
    #     # self.particlesPositions = self.getParticlesPositions()

    #     self.makeWaterfall()
