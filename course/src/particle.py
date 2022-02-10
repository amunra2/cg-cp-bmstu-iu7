import numpy as np
from random import random, randint
import glm

from consts import *

from copy import deepcopy

acceleration = 0.00098
initialDirection = [0.0, -0.2, -1.0]

def setParticleSpeed(value):
    global acceleration

    acceleration = (value / 100000)

    print(acceleration)

    # if (operation == MORE):
    #     acceleration *= VALUE_CHANGE
    # elif (operation == LESS):
    #     acceleration /= VALUE_CHANGE


def setParticleAngle(value):
    global initialDirection

    initialDirection[1] = value / 10   


class Particle:
    directionVariance = [0.2, -0.3, 0.1]

    diameterMean = 0.5
    diameterVariance = 0.05

    speedMean = 0.00001
    speedVariance = 0.000001

    waterColour = [0, 153, 204, 1]
    accelerationGravity = 0.00098
    gravityDirection = [0.0, -0.1, 0.0]

    windScale = 1000.0
    windDirection = [-1.0, 0.0, 0.0]

    num = 0
    check = True


    def __init__(self, lineStart, lineEnd):

        self.pos = self.initialParticlePosition(lineStart, lineEnd)
        self.speed = self.speedMean + random() * self.speedVariance

        wind = self.scalarMul(self.windDirection, self.windScale) # вектор * скаляр
        self.direction = self.addDirections(self.initialParticleDirection(), wind)

        self.age = 0
        self.maxAge = randint(100, 700)
        self.color = self.initColor()

        self.acceleration = acceleration


    def addDirections(self, dirA, dirB): # может быть надо будет поменять на обе dirA
        return [dirA[0] + dirA[0],
                dirA[1] + dirA[1],
                dirA[2] + dirA[2]]
    

    def initialParticleDirection(self):
        direction = deepcopy(initialDirection)

        direction[0] += (random() * self.directionVariance[0])
        direction[1] += (random() * self.directionVariance[1])
        direction[2] += (random() * self.directionVariance[2])

        return direction


    def initialParticlePosition(self, lineStart, lineEnd):
        vector = [lineEnd[0] - lineStart[0],
                  lineEnd[1] - lineStart[1],
                  lineEnd[2] - lineStart[2]]

        randNum = random()

        initPos = [lineStart[0] + vector[0] * randNum,
                   lineStart[1] + vector[1] * randNum,
                   lineStart[2] + vector[2] * randNum]

        return initPos


    def scalarMul(self, vec, num):
        return [vec[0] * num,
                vec[1] * num,
                vec[2] * num]


    def getPosition(self):
        pos = np.array((self.pos[0], self.pos[1], self.pos[2]), dtype = 'float32')
        return pos


    def initColor(self):
        if (random() > 0.5):
            initedColor = glm.vec4(0, 0.584, 0.713, 1)
        else:
            initedColor = glm.vec4(0.450, 0.713, 0.996, 1)

        return initedColor


    def getColor(self):
        return self.color


    def moveWaterfallParticle(self):
        oldSpeed = self.speed
        oldDirection = deepcopy(self.direction)

        self.direction[0] += self.gravityDirection[0]
        self.direction[1] += self.gravityDirection[1]
        self.direction[2] += self.gravityDirection[2]

        self.speed += self.acceleration

        self.pos[0] += (oldSpeed * oldDirection[0] + self.speed * self.direction[0])
        self.pos[1] += (oldSpeed * oldDirection[1] + self.speed * self.direction[1])
        self.pos[2] += (oldSpeed * oldDirection[2] + self.speed * self.direction[2])

        self.age += 1


        if (self.pos[1] <= -14.7):
            self.speed = 0.8 * self.speed
            self.pos[0] -= (oldSpeed * oldDirection[0] + self.speed * self.direction[0])
            self.pos[1] -= (oldSpeed * oldDirection[1] + self.speed * self.direction[1])
            self.pos[2] -= (oldSpeed * oldDirection[2] + self.speed * self.direction[2])
            self.color = glm.vec4(1, 1, 1, 1)

        if (self.age + 150 > self.maxAge):
            self.color = glm.vec4(1, 1, 1, 1)

        return self


    def moveSolidParticle(self):
        oldSpeed = self.speed
        oldDirection = deepcopy(self.direction)

        self.direction[0] += self.gravityDirection[0]
        self.direction[1] += self.gravityDirection[1]
        self.direction[2] += self.gravityDirection[2]

        self.speed += self.acceleration

        self.pos[0] += (oldSpeed * oldDirection[0] + self.speed * self.direction[0])
        # self.pos[1] += (oldSpeed * oldDirection[1] + self.speed * self.direction[1])
        self.pos[2] += (oldSpeed * oldDirection[2] + self.speed * self.direction[2])

        self.age += 1

        if (self.age + 150 > self.maxAge):
            self.color = glm.vec4(1, 1, 1, 1)

        return self 

        

