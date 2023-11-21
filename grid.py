from params import *
from scipy.ndimage import zoom, gaussian_filter
from numpy.random import uniform, randint
from numpy import pi

# -----------------------------------------------
#                   GRID MAP
# -----------------------------------------------

# convert character into a grayscale value
charToValueDict = {'#': 1,
                   '*': .5,
                   '.': 0,
                   ' ': 0}


def loadGridFromFile(WorldName):
    # reads a .txt file into a numpy matrix
    FILEPATH = WORLD_PATH / (WorldName + ".txt")
    with open(FILEPATH, mode='r') as file:
        grid = []
        for (i, line) in enumerate(file.readlines()):
            if not line.startswith("//"):  # comment
                row = []
                for char in line:
                    if not char == "\n":
                        row.append(charToValueDict[char])
                grid.append(row)
        file.close()
    return np.array(grid)


def loadWorld(worldName, size):
    originalGrid = loadGridFromFile(worldName)  # load world
    zoomFaktor = size / originalGrid.shape[0]
    zoomedGrid = zoom(originalGrid, zoomFaktor).astype(float)  # zoom world to size
    return gaussian_filter(zoomedGrid, sigma=3)  # run gauss filter to blur edges


# WORLD: changed when loading world
GRID = loadWorld(WORLD_NAME, size=WORLD_SIZE)
HEIGHT, WIDTH = np.shape(GRID)

isWall = lambda x,y: GRID[y, x] > WALL_THRESH

def findValidCoords():
    # returns all valid positions of grid
    # valid means white or close to white, aka not a wall
    validCoords = []
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if not isWall(x,y):
                validCoords.append([x, y])
    return np.array(validCoords)


VALID_COORDS = findValidCoords()


def randomPosition():
    # puts robot to a random new position in the grid
    # this methode is needed form resampling and kidnapping
    phi = 2 * pi * uniform()
    randomIndex = randint(0, len(VALID_COORDS))
    x, y = VALID_COORDS[randomIndex]
    return x, y, phi
