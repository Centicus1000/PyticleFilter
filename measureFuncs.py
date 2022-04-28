from params import *
from numpy import cos, sin, pi, abs

# -----------------------------------------------
#             MEASURING ALGORITHMS
# -----------------------------------------------

def bresenham(startCoords, angle, shouldStopFunc):
    # BRESENHAM ALGORITHM: this method implements bresenham's algorithm to determine a distance inputs are starting
    # coordinates x and y and rotational angle phi with 0 being looking left and positive angle movement is turning
    # left. ACHTUNG: since x and y represent indices in GRID map the y coordinate is going down instead of up.
    # That's why 'sy' signs are reversed. ShouldStopFunc is a method taking a coordinate tuple (x,y) and returning a
    # Bool value whether bresenham should stop. Because the end-Coordinates are unknown the algorithm just needs a
    # direction (angle) and a function telling him to stop or not, that is called every step. Once shouldStopFunc
    # returns True (which it should eventually) the current x and y values are the desired end-Coordinates and the
    # distance to the start-Coordinates can be calculated.

    currX, currY = startCoords
    angle %= 2 * pi
    dx = abs(100 * cos(angle))  # angle in dx und dy umrechnen
    dy = -abs(100 * sin(angle))

    sx = -1 if (pi / 2) <= angle < (3 * pi / 2) else 1
    sy = -1 if 0 <= angle < pi else 1
    err = dx + dy

    while not shouldStopFunc([int(currX), int(currY)]):
        e2 = 2 * err
        if e2 > dy:
            err += dy
            currX += sx
        if e2 < dx:
            err += dx
            currY += sy

    # calculate magnitude of the difference vektor between start and stop -> distance
    return np.linalg.norm(np.array([currX, currY]) - np.array(startCoords))


def sinCosCounter(startCoords, angle, shouldStopFunc):
    # SINUS & COSINUS - COUNTER: this method solves the same problem as bresenham but in a less efficient way,
    # it was use in an older version of this code. Run this file to compare runtime (main below). It uses a counter (
    # dist) that count up by one every step. With sin, cos and the angle the corresponding indices can be
    # calculated. Checking for Wall, or for a condition to stop, works in the same way as bresenham: The
    # shouldStopFunction is called every step until it returns True. Disadvantages are the the dist value will only be
    # integer values and with sin and cos some x,y-Combinations are checked twice (inefficient).

    dist = 0
    currX, currY = startCoords
    while not shouldStopFunc([currX, currY]):
        currX = int(startCoords[0] + dist * cos(angle) + .5)
        currY = int(startCoords[1] - dist * sin(angle) + .5)
        dist += 1

    return np.abs(np.array([currX, currY] - np.array(startCoords)))


if __name__ == '__main__':
    # COMPARING RUNTIME run this file to compare runtime between the to algorithms. Here is how is works: The start
    # position is constant [x=0, y=0]. An counter i count up to a certain high number (e.g. 2000). At every step the
    # end-Coordinates are at a distance of i and at an angle of i/2, so pseudo-randomly spiraling outwards,
    # making it harder and harder to reach the desired end and at same same time trying out (more or less) every
    # possible angle. The times the algos needed to solve the problem ist the plotted to compare.

    import matplotlib.pyplot as plt
    from numpy import arctan2
    import time

    b_times = []
    s_times = []

    # Laufzeit analyse
    for i in range(10, 2000, 10):
        start = [0, 0]
        stop = [int(i * cos(i / 2) + .5),
                int(i * sin(i / 2) + .5)]


        def check(currPos):
            xSrt, ySrt = currPos
            xEnd, yEnd = stop
            return abs(xSrt) >= abs(xEnd) and abs(ySrt) >= abs(yEnd)

        startTime = time.perf_counter()
        bresenham(start, arctan2(stop[1], stop[0]), shouldStopFunc=check)
        stopTime = time.perf_counter() - startTime
        b_times.append(stopTime)

        startTime = time.perf_counter()
        sinCosCounter(start, arctan2(stop[1], stop[0]), shouldStopFunc=check)
        stopTime = time.perf_counter() - startTime
        s_times.append(stopTime)



    plt.plot(b_times)
    plt.plot(s_times)
    plt.legend(["Bresenham", "SinCos Counter"])
    plt.show()
