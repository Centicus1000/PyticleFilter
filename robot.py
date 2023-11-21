# -----------------------------------------------
#                     ROBOT
# -----------------------------------------------
import numpy as np

from numpy import sin, cos, tanh, pi, arctanh
from numpy.random import normal

from params import *
from measureFuncs import bresenham
from grid import *
from mrc import MinimalRecurrentController

motorNoise = lambda: normal(loc=0.0, scale=MOTOR_NOISE_FAK)  # zufalls normalverteilung
sensorNoise = lambda: normal(loc=0.0, scale=SENSOR_NOISE_FAK)  # zufalls normalverteilung


class Robot(object):

    def __init__(self, startPos=None):
        if startPos is None:
            # if no start postion is provided the robot is put to a random valid position on the grid
            startPos = randomPosition()
        self.x, self.y, self.phi = startPos
        self.fixPosition()
        self.mrc = MinimalRecurrentController()  # automatic navigation in world
        self.lastDist = 0  # remember last measured distance to save runtime
        # plotting objects
        self.selfPlot = None
        self.distPlot = None

    # MEASURING
    def measure(self):
        # MEASURES DISTANCE TO WALL: simulating a distance senor that is looking straight ahead. the methode measures
        # the distance to the closed wall inside the GRID map that the sensor should pick up and adds a little noise.
        def isWall(coords):
            # shouldStopFunction for bresenham, returns true when wall is reached
            # checks in grid if coords are in fact a wall -> True else False
            x, y = coords
            return GRID[y % HEIGHT, x % WIDTH] > .5

        realDist = bresenham(startCoords=[self.x, self.y],
                             angle=self.phi,
                             shouldStopFunc=isWall, )
        self.lastDist = realDist * (1. + sensorNoise())
        return self.lastDist

    def normalizedDist(self):
        # puts sensor into normalized range: -1 < sensor value < +1
        # helps the robot (the MRC) to decide when too turn / how close to drive to a wall
        # -1 = no wall, 0 = MIN_WALL_DISTANCE, +1 = wall (not good)
        return -tanh((self.lastDist - MIN_WALL_DISTANCE) / - arctanh(-0.999))

    # MOVING
    def isInWall(self):
        return isWall(int(self.x), int(self.y))

    def moveTo(self, newPos):
        # move robot safely to different position
        x, y, phi = newPos
        self.x = x
        self.y = y
        self.phi = phi
        self.fixPosition()

    def fixPosition(self):
        # when moving outside of bounds: wrap around
        self.x %= WIDTH
        self.y %= HEIGHT
        self.phi %= 2 * pi

    def moveBy(self, mL, mR):
        # update x,y,phi (odometry)
        deltaPhi = ROBOT_SPEED * ((mR - mL) + motorNoise()) / ROBOT_SIZE
        deltaX = ROBOT_SPEED * (cos(self.phi) * (mR + mL) / 2 + motorNoise())
        deltaY = ROBOT_SPEED * (-sin(self.phi) * (mR + mL) / 2 + motorNoise())
        newPos = (self.x + deltaX, self.y + deltaY, self.phi + deltaPhi)
        self.moveTo(newPos)

    def autoDrive(self):
        # run MRC one step
        self.mrc.step(sensor=self.normalizedDist())
        mL, mR = self.motorSignals()
        self.moveBy(mL, mR)

    def motorSignals(self):
        # returns current outputs of controller network
        return self.mrc.motorSignals()

    # PLOTTING
    def bodyCoords(self):
        trianglePath = np.array([[0, ROBOT_SIZE / 3],  # left wheel
                                 [0, -ROBOT_SIZE / 3],  # right wheel
                                 [ROBOT_SIZE, 0],  # front
                                 [0, ROBOT_SIZE / 3]])  # left wheel again

        offsetVektor = np.array([self.x, self.y])
        rotationMatrix = np.array([[cos(self.phi), -sin(self.phi)],
                                   [sin(self.phi), cos(self.phi)]])
        affineTransform = lambda vektor: np.matmul(vektor, rotationMatrix) + offsetVektor

        for i in np.arange(len(trianglePath)):
            trianglePath[i] = affineTransform(trianglePath[i])

        return trianglePath[:, 0], trianglePath[:, 1]

    def initSelfPlot(self):
        Rx, Ry = self.bodyCoords()  # coords of triangle form
        self.selfPlot, = plt.plot(Rx, Ry, "b-")
        return self.selfPlot

    def updateSelfPlot(self, externPlot=None):
        if externPlot is not None:
            self.selfPlot = externPlot
        Rx, Ry = self.bodyCoords()
        self.selfPlot.set_data(Rx, Ry)
