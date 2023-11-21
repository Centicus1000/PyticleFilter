from matplotlib.animation import FuncAnimation
from grid import *
from particlefilter import ParticleFilter
from robot import Robot
from time import perf_counter as currentTime

# GLOBAL Todos-list:
# todo: einen vernünftigen plot mit einstellbaren plots
# todo: Laufzeit analyse / optimierung
# todo: adjustable and more flexible resampling
# todo: adaptive resampling noise
# todo: observer / overall fitness criteria
# todo: bessere klassen / file -Beschreibungen
# todo: hübsches Readme
# todo: TCPIP / Webots connection

# ----------------------------------------------
#                MAIN SKRIPT
# ----------------------------------------------

if __name__ == '__main__':
    loopCounter = 0
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 6),
                           gridspec_kw={
                               'width_ratios': [3, 1],
                               'height_ratios': [3],
                               'wspace': 0.4,
                               'hspace': 0.4})

    # plot the world
    plt.subplot(121)
    plt.imshow(GRID, cmap="Greys")
    plt.xlim([0, WIDTH])
    plt.ylim([HEIGHT, 0])

    # initialise simulation of the real robot
    robbi = Robot()
    robbi.initSelfPlot()

    # initialise the particle filter
    pf = ParticleFilter()
    pf.initPlot()

    plt.subplot(122)
    pf.initWeightPlot()


    def mainLoop(i):
        global loopCounter, avgRuntime, maxRuntime
        loopCounter += 1

        # move robot, pf make proposal
        robbi.autoDrive()
        pf.moveAll(robbi.motorSignals())
        # robot measures, pf makes correction
        realDist = robbi.measure()
        pf.measureAll(realDist)
        # update plots
        robbi.updateSelfPlot()
        pf.updatePlot()

        pf.autoResample(loopCounter)

        if np.average(pf.weights) > AVG_W_QUIT_THRESH:
            robbi.moveTo(randomPosition())


    ani = FuncAnimation(fig, mainLoop, interval=TIME_STEP, repeat=True)
    plt.show()
