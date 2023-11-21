from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------
#                  PARAMETER
# ----------------------------------------------

# this file contains all parameters of this project, so tweaking and optimizing cna be done by changing values her
# instead of having to search through the whole project. The parameter are written in ALL CAPS so they're easily
# spotted.


# Grid World params
WORLD_NAME = "simon"
WORLD_SIZE = 200  # points (height of gridMap)
WORLD_PATH = Path(".") / "worlds"  # path of folder containing example world files
TIME_STEP = 10  # ms, delay between frames (matplotlib animation)
WALL_THRESH = 0.3  # minimal pixel value that counts as wall
AVG_W_QUIT_THRESH = 0.95 # triggers das auto kidnap

# Robot Params
ROBOT_SIZE = 4.  # points, length back to front, height of plotted triangle
ROBOT_SPEED = 1.5  # points per step
MIN_WALL_DISTANCE = 10  # threshold distance of wall before going backwards in pixels
MOTOR_NOISE_FAK = 0.01  # in %, gets added onto the motor signals when moving
SENSOR_NOISE_FAK = 0.01  # in %, gets added onto the sensor signal when measuring
SHOULD_KIDNAP = True  # Kidnapping on off

# MRC Parameter
OSCI_WEIGHTS = np.array([[0.8, -0.6], [1.9, 2.0]])
OSCI_W11, OSCI_W12 = OSCI_WEIGHTS[0]
OSCI_W21, OSCI_W22 = OSCI_WEIGHTS[1]

MRC_WEIGHTS = np.array(([2., -5.]))
MRC_W_SELF, MRC_W_ACROSS = MRC_WEIGHTS

MRC_TURN_RATIO = 0.35  # in %, ratio between network output and turn output (osci)

# Partikel Filter Params
NUM_OF_PARTIKELS = 200
RESAMPLE_FREQ = 10  # samples per loop, should be smaller that num of partikels
INIT_PARTIKEL_WEIGHT = 0.5  # weight after initialization and after resampling
GOOD_THEORY_THRESH = 0.65  # weight threshold value, if bigger -> good theory
RESAMPLE_NOISE = 0.02
RESAMPLE_METHOD = 'hva'

HOLE_WIDTH = 10  # points, tolerance of measured signal, deviation -> gauss function
STUBBORNNESS = 0.95  # adaptive parameter of weights, with values closer the weights are updated slower
PARTIKEL_SIZE_FAK = 1  # is multiplied by the weights -> size of partikels in scatter plot
SCAN_MATCHING = 0.7  # in %, how strongly the partikels adjust their postion to better fit the measurement
