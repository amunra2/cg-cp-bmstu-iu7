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
from random import random, shuffle, choice
from copy import deepcopy

from shader import Shader

from object import Object
from camera import Camera

from particle import Particle



class winGL(QtOpenGL.QGLWidget):
    newParticlesMean = 50.0
    newParticlesVariance = 5.0

    active = True

    maxAge = 70

    # Водопад
    lineStartWF = [-10, 0, 0]
    lineEndWF   = [ 10, 0, 0]

    # Скала
    lineStartRock = [-10, 0, 5]
    lineEndRock   = [ 10, 0, 5]

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

        self.waterfallReady = False

        # Для частиц водопада и водяного потока
        self.particlesNum = 1000

        self.waterfallParticles = self.createParticles(self.lineStartWF, self.lineEndWF)
        self.solidParticles = self.createParticles(self.lineStartRock, self.lineEndRock)
        self.allParticles = self.getAllParticles()

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

        # print("VRTXS1: ", type(self.vrtxs1[0]))

        # self.vrtxs2 = np.array(
        # ((-0.5, -0.5, 0),
        #  ( 0.5, -0.5, 0),
        #  ( 0.5,  0.5, 0),
        #  (-0.5,  0.5, 0)
        # ),
        # dtype='float32')

        
        # Скала
        self.solidRock = np.array(
        (
            (-10,   -0.01,  0),
            (-10,   -0.01,  5),
            ( 10,   -0.01,  5),
            ( 10,   -0.01,  0),

            (-10, -15,  0),
            (-10, -15,  5),
            ( 10, -15,  5),
            ( 10, -15,  0)
        ), 
        dtype = 'float32')

        self.indicesRock = np.array((0, 1, 3, 1, 2, 3,
                                     4, 5, 7, 5, 6, 7,
                                     0, 3, 4, 3, 4, 7,
                                     1, 2, 5, 2, 5, 6,
                                     0, 1, 4, 1, 4, 5,
                                     2, 3, 6, 3, 6, 7), dtype='int32')

        self.colorRock = [
            # glm.vec4(0.396, 0.262, 0.129, 1),
            # glm.vec4(0.396, 0.262, 0.129, 1),
            # glm.vec4(0.396, 0.262, 0.129, 1),
            # glm.vec4(0.396, 0.262, 0.129, 1),
            glm.vec4(0.396, 0.262, 0.129, 1),
            glm.vec4(0.396, 0.262, 0.129, 1),
            glm.vec4(0.396, 0.262, 0.129, 1),
            glm.vec4(0.396, 0.262, 0.129, 1)
        ]

        self.colorRock = np.array(self.colorRock, dtype = "float32")


        # Test
        self.solidTest = np.array(
        (
            (-10, 0.1, 0), #  0
            ( -6, 0.1, 0), #  1
            ( -2, 0.1, 0), #  2
            (  2, 0.1, 0), #  3
            (  6, 0.1, 0), #  4
            ( 10, 0.1, 0), #  5
 
            (-10, 0.1, 3), #  6
            ( -6, 0.1, 3), #  7
            ( -2, 0.1, 3), #  8
            (  2, 0.1, 3), #  9
            (  6, 0.1, 3), # 10
            ( 10, 0.1, 3), # 11
 
            (-10, 0.1, 6), # 12
            ( -6, 0.1, 6), # 13
            ( -2, 0.1, 6), # 14
            (  2, 0.1, 6), # 15
            (  6, 0.1, 6), # 16
            ( 10, 0.1, 6), # 17
        ), 
        dtype = 'float32')

        self.solidTest = self.getCords(5, 15, [-15, -14.9, -20], 2, 5)
        self.solidTest = np.array(self.solidTest, dtype = "float32")
        

        self.indicesTest = self.getIndices(5, 15)
        self.indicesTest = np.array(self.indicesTest, dtype = "int32")

        self.colorTest = [
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(1, 1, 1, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0.450, 0.482, 0.490, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0, 0.584, 0.713, 1),

            glm.vec4(0.450, 0.482, 0.490, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(1, 1, 1, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0.450, 0.482, 0.490, 1),
            glm.vec4(0, 0.584, 0.713, 1),

            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0.450, 0.482, 0.490, 1),
            glm.vec4(0.450, 0.482, 0.490, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(1, 1, 1, 1)
        ]

        self.colorTest = self.getColor(5, 15)

        self.colorTestNP = np.array(self.colorTest, dtype = "float32")


        # Озеро
        self.solidLake = np.array(
        (
            (-15, -15,   5),
            (-15, -15, -20),
            ( 15, -15, -20),
            ( 15, -15,   5),

            (-15, -20,   5),
            (-15, -20, -20),
            ( 15, -20, -20),
            ( 15, -20,   5)
        ), 
        dtype = 'float32')

        self.indicesLake = np.array((0, 1, 3, 1, 2, 3,
                                     4, 5, 7, 5, 6, 7,
                                     0, 3, 4, 3, 4, 7,
                                     1, 2, 5, 2, 5, 6,
                                     0, 1, 4, 1, 4, 5,
                                     2, 3, 6, 3, 6, 7), dtype='int32')

        self.colorLake = [
            # glm.vec4(0.396, 0.262, 0.129, 1),
            # glm.vec4(0.396, 0.262, 0.129, 1),
            # glm.vec4(0.396, 0.262, 0.129, 1),
            # glm.vec4(0.396, 0.262, 0.129, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0, 0.584, 0.713, 1),
            glm.vec4(0, 0.584, 0.713, 1)
        ]

        self.colorLake = np.array(self.colorLake, dtype = "float32")


    def getColor(self, height, width):

        colors = []

        colorTypes = [glm.vec4(0, 0.584, 0.713, 1),
                      glm.vec4(0.450, 0.713, 0.996, 1)]


        for i in range((height + 1) * (width + 1)):
            element = choice(colorTypes)
            colors.append(element)

        return colors


    def getIndices(self, height, width):
        
        allIndices = []

        for i in range(height):

            indices = []

            for j in range(width):
                indices.append((i * (width + 1)) + j)
                indices.append((i * (width + 1)) + (j + 1))
                indices.append(((i + 1) * (width + 1)) + (j + 1))

                indices.append((i * (width + 1)) + j)
                indices.append(((i + 1) * (width + 1)) + j)
                indices.append(((i + 1) * (width + 1)) + (j + 1))

            if (i % 2 == 1):
                indices.reverse()

            allIndices.extend(indices)

        # print(allIndices)

        return allIndices


    def getCords(self, height, width, cord, stepX, stepZ):

        cords = []

        x = cord[0]
        y = cord[1]
        z = cord[2]

        for i in range(0, height + 1):
            for j in range(0, width + 1):
                cords.append(np.array((x + j * stepX, y, z + i * stepZ), dtype = "float32"))

        # print(cords)

        return cords


    def initializeGL(self):
        print("START Init")
        self.qglClearColor(QtGui.QColor(50, 50, 50))
        gl.glEnable(gl.GL_DEPTH_TEST)


    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.camera.changePerspective(ratio = width / height)
        self.camera.setPos([-20, 5, 0])
        self.camera.spinY(90)


    def paintSolidObject(self, vrtxs, indices, color):
        cubeVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, cubeVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vrtxs, gl.GL_STATIC_DRAW)

        cubeEBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, cubeEBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)
        
        cubeColorVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, cubeColorVBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, color, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
        gl.glEnableVertexAttribArray(0)

        gl.glEnableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, cubeColorVBO)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, True, 0, None)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, cubeEBO)

        gl.glDrawElements(gl.GL_TRIANGLES, 1000, gl.GL_UNSIGNED_INT, None)

        gl.glDisableVertexAttribArray(0)
        gl.glDisableVertexAttribArray(1)


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

        # Скала
        self.paintSolidObject(self.solidRock, self.indicesRock, self.colorRock)

        # Озеро
        self.paintSolidObject(self.solidLake, self.indicesLake, self.colorLake)

        # Test
        self.paintSolidObject(self.solidTest, self.indicesTest, self.colorTestNP)





        # Водопад
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
        gl.glVertexAttribDivisor(1, 0)

        gl.glPointSize(5)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self.allParticles))

        # print("Particles = ", len(self.allParticles))


    def getAllParticles(self):
        allParticles = []
        if (self.waterfallReady):
            allParticles.extend(self.waterfallParticles)
        allParticles.extend(self.solidParticles)

        return allParticles


    def createParticles(self, lineStart, lineEnd):

        particles = []

        for i in range(self.particlesNum):
            particles.append(Particle(lineStart, lineEnd))

        return particles
        
    
    def getParticlesColor(self):
        colors = []

        check = True
        num = 0

        for particle in self.allParticles:
            colors.append(particle.getColor())

        npColors = np.array(colors)
        

        return npColors


    def getParticlesPositions(self):
        positions = []
        colors = []

        for particle in self.allParticles:
            positions.append(particle.getPosition())
            colors.append(particle.getColor())

        self.particlesColors = np.array(colors)
        poses = np.array(positions)

        return poses


    def moveParticles(self):
        
        if (self.waterfallReady):
            for particle in self.waterfallParticles:
                particle.moveWaterfallParticle()

        for particle in self.solidParticles:
            particle.moveSolidParticle()

        self.allParticles = self.getAllParticles()

        self.particlesPositions = self.getParticlesPositions()
        self.particlesColors = self.getParticlesColor()
        

    def makeWaterfall(self):
        # print("Particles: ", len(self.particles))
        
        self.deleteExtraParticles()

        # Добавить еще частиц
        extraParticlesNum = int(self.newParticlesMean + random() * self.newParticlesVariance)

        for i in range(extraParticlesNum):
            self.waterfallParticles.append(Particle(self.lineStartWF, self.lineEndWF))

        for i in range(int(extraParticlesNum * 1.5)):
            self.solidParticles.append(Particle(self.lineStartRock, self.lineEndRock))

        self.particlesNum += extraParticlesNum

        # Обновить атрибуты для всех частиц
        self.moveParticles()


    def deleteExtraParticles(self):
        deletedParticles = 0

        # Удалить упавшие капли
        for particle in self.waterfallParticles:
            if (particle.age > particle.maxAge):
                self.waterfallParticles.pop(0)
                # self.particles.append(Particle())
                deletedParticles += 1

        for particle in self.solidParticles:
            if (particle.pos[2] < 0):
                self.waterfallReady = True
                self.solidParticles.pop(0)
                # self.particles.append(Particle())
                deletedParticles += 1

        
        self.allParticles = self.getAllParticles()

        self.particlesNum -= deletedParticles
    

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

        # print(self.lastPos)

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


    def updateWaterColor(self):
        np.random.shuffle(self.colorTestNP)




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