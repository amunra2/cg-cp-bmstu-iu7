import glm

from object import Object


class Camera(Object):
    def __init__(self, angle = 45, ratio = 1, near = 0.01, far = 100):
        super().__init__()

        self.angle = angle
        self.ratio = ratio
        self.near = near
        self.far = far

        self.pos = glm.vec3()

        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3()

        self.pitch = 0.0
        self.yaw = -90.0
        self.roll = 0.0

        self.worldUp = glm.vec3(0, 1, 0)
        self.speed = 0.04
        self.sensivity = 0.05

        self.__updateVectors()

    def __updateVectors(self):
        sinYaw, cosYaw = (glm.sin(glm.radians(self.yaw)),
                          glm.cos(glm.radians(self.yaw)))
        sinPitch, cosPitch = (glm.sin(glm.radians(self.pitch)),
                          glm.cos(glm.radians(self.pitch)))
        sinRoll, cosRoll = (glm.sin(glm.radians(self.roll)),
                          glm.cos(glm.radians(self.roll)))

        newFront = glm.vec3()

        newFront.x = cosYaw * cosPitch
        newFront.y = sinPitch
        newFront.z = sinYaw * cosPitch

        self.front = glm.normalize(newFront)
        self.right = glm.normalize(glm.cross(self.front, self.worldUp))
        self.up = glm.normalize(glm.cross(self.right, self.front))


    def getProjMatrix(self):
        return glm.perspective(glm.radians(self.angle), self.ratio, self.near, self.far)

    def getViewMatrix(self):
        return glm.lookAt(self.pos, self.pos + self.front, self.up)

    def setPos(self, pos):
        self.pos = glm.vec3(*pos)

    def translate(self, x, y, z):
        self.pos += glm.vec3(x, y, z)

    def spinX(self, angle):
        self.pitch += angle
        self.__updateVectors()

    def spinY(self, angle):
        self.yaw += angle
        self.__updateVectors()

    def spinZ(self, angle):
        self.roll += angle
        self.__updateVectors()

    def spinByAxis(self, axis, angle):
        super().spinByAxis(axis, angle)

    def changePerspective(self, angle = 45, ratio = 1, near = 0.01, far = 100):
        self.angle = angle
        self.ratio = ratio
        self.near = near
        self.far = far

    def continousTranslate(self, directions):
        self.pos += self.speed * self.front * directions["w"]
        self.pos -= self.speed * self.front * directions["s"]
        self.pos += (self.speed * glm.normalize(glm.cross(self.pos, self.up)) * directions["a"])
        self.pos -= (self.speed * glm.normalize(glm.cross(self.pos, self.up)) * directions["d"])

    def rotation(self, deltaX, deltaY):
        self.yaw += deltaX + self.sensivity
        self.pitch += deltaY + self.sensivity

        if (self.pitch > 89.0):
            self.pitch = 89.0

        if (self.pitch < -89.0):
            self.pitch = -89.0

        self.__updateVectors()

    def zoom(self, k):
        self.angle -= k

        if (self.angle < 1.0):
            self.angle = 1.0

        if (self.angle > 100.0):
            self.angle = 100.0
