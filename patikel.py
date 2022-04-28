from params import *
from numpy import pi, exp
from numpy.random import normal
from grid import WIDTH, HEIGHT, randomPosition
from robot import Robot


# ----------------------------------------------
#              (SINGLE) PARTIKEL
# ----------------------------------------------

class Partikel(Robot):

    def __init__(self):
        super().__init__()

    def coords(self):
        # own coordinates, phi is ignored here
        return [self.x, self.y]

    def confidence(self, realDist):
        # check if own Distance fits the real Distance
        selfDist = self.measure()
        conf = exp(-((selfDist - realDist) / HOLE_WIDTH) ** 2)  # 1D-RBF-Function
        deltaConf = 2 * (selfDist - realDist) / HOLE_WIDTH * conf  # derivativ of partikel to adjust its position
        adjMotor = SCAN_MATCHING * ROBOT_SPEED * deltaConf
        self.moveBy(adjMotor, adjMotor)  # moves partikel forward/backwards to better fit measurement net time
        return conf

    # RESAMPLING PARTIKEL
    def resampleToRandom(self):
        self.moveTo(randomPosition())

    def resampleTo(self, otherPartikel, noise=RESAMPLE_NOISE):
        # move partikel at position of another partikel with some noise
        self.x = normal(otherPartikel.x, WIDTH * noise)
        self.y = normal(otherPartikel.y, HEIGHT * noise)
        self.phi = normal(otherPartikel.phi, 2 * pi * noise)
        self.fixPosition()
