import numpy as np
from random import random, randint
import glm

from copy import deepcopy


WATER_LINE = -14.7
BOUNCE_COEF = 0.15


speedMean = 0.00001
speedVariance = 0.000001
initialDirection = [0.0, -0.2, -1.0]



def setParticleSpeed(value):
    global speedMean, speedVariance

    speedMean = (value / 10000)
    speedVariance = (value / 100000)


def setParticleAngle(value):
    global initialDirection

    initialDirection[1] = value / 10   


class Particle:
    directionVariance = [0.2, -0.3, 0.1]

    waterColour = [0, 153, 204, 1]
    accelerationGravity = 0.00098
    gravityDirection = [0.0, -0.1, 0.0]

    windScale = 1.0
    windDirection = [0.0, 0.0, -1.0]

    num = 0
    check = True

    vaporized = False


    def __init__(self, lineStart, lineEnd):

        # Вычисление координаты частицы
        self.pos = self.initialParticlePosition(lineStart, lineEnd)

        # Вычисление скорости частицы (случайным образом
        # на основании наличия начальной скорости + случайным добавление скорости)
        self.speed = speedMean + random() * speedVariance

        # Вектор направления движения ветра
        # (начальный вектор * коэффициент скорости ветра)
        wind = self.scalarMul(self.windDirection, self.windScale) # вектор * скаляр

        # Направление движения частицы
        # Сложение двух векторов: случайного направления вектора в плоскости OYZ +
        # вектора движения ветра 
        self.direction = self.addDirections(self.initialParticleDirection(), wind)

        # Текущее время жизни частицы
        # (при достижении максимального значения - удаляется)
        self.age = 0

        # Максимальное время жизни частицы определяется рандомным образом
        self.maxAge = randint(100, 700)

        # Случайный цвет частицы
        self.color = self.initColor()

        # Заданное ускорение движения частицы
        # (ускорение свободного падения)
        self.acceleration = self.accelerationGravity


    def addDirections(self, dirA, dirB):
        # Сложение двух векторов
        # (для вектора направления движения частицы)
        return [dirA[0] + dirB[0],
                dirA[1] + dirB[1],
                dirA[2] + dirB[2]]
    

    def initialParticleDirection(self):
        # Берется изначально заданное направление движения частицы
        direction = deepcopy(initialDirection)

        # Случайным орбазом движение немного изменяется с целью, чтобы
        # все частицы не падали по одной траектории
        direction[0] += (random() * self.directionVariance[0])
        direction[1] += (random() * self.directionVariance[1])
        direction[2] += (random() * self.directionVariance[2])

        return direction


    def initialParticlePosition(self, lineStart, lineEnd):
        # Вычисление вектора расположения линии водопада
        vector = [lineEnd[0] - lineStart[0],
                  lineEnd[1] - lineStart[1],
                  lineEnd[2] - lineStart[2]]

        randNum = random()

        # Случайная позиция в пределах линии водопада
        initPos = [lineStart[0] + vector[0] * randNum,
                   lineStart[1] + vector[1] * randNum,
                   lineStart[2] + vector[2] * randNum]

        return initPos


    def scalarMul(self, vec, num):
        # Умножение вектора на скаляр
        return [vec[0] * num,
                vec[1] * num,
                vec[2] * num]


    def getPosition(self):
        # Получить позицию частицы в виде нампаевского массива
        pos = np.array((self.pos[0], self.pos[1], self.pos[2]), dtype = 'float32')
        return pos


    def initColor(self):
        # Случайно выбрать цвет частицы из двух
        if (random() > 0.5):
            initedColor = glm.vec4(0, 0.584, 0.713, 1)
        else:
            initedColor = glm.vec4(0.450, 0.713, 0.996, 1)

        return initedColor


    def getColor(self):
        # Получить цвет частицы
        return self.color


    def moveWaterfallParticle(self):
        # Движение частицы в пространстве

        # При достижении водного полотна частица
        # отражается от него, теряя часть скорости и начинает двигаться
        # по иной траектории (в силу отражения) 
        if (self.pos[1] <= WATER_LINE):
            self.speed = BOUNCE_COEF * self.speed
            self.direction[2] *= -1
            self.vaporized = True

        oldSpeed = self.speed
        oldDirection = deepcopy(self.direction)

        self.direction[0] += self.gravityDirection[0]
        self.direction[1] += self.gravityDirection[1]
        self.direction[2] += self.gravityDirection[2]

        if (self.vaporized):

            # Частица, достигшая водного полотна, превращается в водный
            # пар, который по задумке белого цвета
            self.color = glm.vec4(1, 1, 1, 1)

            self.speed -= self.acceleration

            self.pos[0] = self.pos[0] + oldSpeed * oldDirection[0] + (self.speed * self.direction[0]) / 2 # (+ oldSpeed * oldDirection[0])? Нужно ли это и зачем?
            self.pos[1] = self.pos[1] - (oldSpeed * oldDirection[1] + (self.speed * self.direction[1]) / 2)
            self.pos[2] = self.pos[2] - (oldSpeed * oldDirection[2] + (self.speed * self.direction[2]) / 2)
        else:
            self.speed += self.acceleration

            self.pos[0] = self.pos[0] + oldSpeed * oldDirection[0] + (self.speed * self.direction[0]) / 2 # (+ oldSpeed * oldDirection[0])? Нужно ли это и зачем?
            self.pos[1] = self.pos[1] + oldSpeed * oldDirection[1] + (self.speed * self.direction[1]) / 2
            self.pos[2] = self.pos[2] + oldSpeed * oldDirection[2] + (self.speed * self.direction[2]) / 2

        # Время жизни частицы + 1
        self.age += 1

        # Если время жизни частицы близко к максимальному, то
        # красить частицу в белый и замедлить ее, поскольку она превращается
        # в пар и отлетает от водопада (брызги)
        if (self.age + 100 > self.maxAge):
            self.speed *= 0.9
            self.direction[2] *= 1.014
            self.color = glm.vec4(1, 1, 1, 1)

        return self

    # То же самое, что и движение водопада, только для текучего потока
    # (не изменяется координата по Y, возможно стоит объединить в одну функцию)
    def moveSolidParticle(self):

        oldSpeed = self.speed
        oldDirection = deepcopy(self.direction)

        self.direction[0] += self.gravityDirection[0]
        self.direction[1] += self.gravityDirection[1]
        self.direction[2] += self.gravityDirection[2]

        self.speed += self.acceleration

        self.pos[0] = self.pos[0] + oldSpeed * oldDirection[0] + (self.speed * self.direction[0]) / 2 # (+ oldSpeed * oldDirection[0])? Нужно ли это и зачем?
        self.pos[2] = self.pos[2] + oldSpeed * oldDirection[2] + (self.speed * self.direction[2]) / 2

        self.age += 1

        if (self.age + 150 > self.maxAge):
            self.color = glm.vec4(1, 1, 1, 1)

        return self
