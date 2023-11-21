from matplotlib.animation import FuncAnimation

from grid import *
from particlefilter import ParticleFilter
from robot import Robot

# ----------------------------------------------
#                MAIN SKRIPT
# ----------------------------------------------

if __name__ == '__main__':
    # selfPlot erstellen
    loopCounter = 0
    fig, ax = plt.subplots(figsize=(10, 9))

    # echten roboter erstellen
    robbi = Robot()
    robbi.initSelfPlot()

    # 1. subplot
    plt.subplot(221)
    plt.imshow(GRID, cmap="Greys")
    plt.xlim([0, WIDTH])
    plt.ylim([HEIGHT, 0])
    plt.title("rws")
    robiPlot1 = robbi.initSelfPlot()
    pf1 = ParticleFilter()
    pf1.initPlot()

    # 2. subplot
    plt.subplot(222)
    plt.imshow(GRID, cmap="Greys")
    plt.xlim([0, WIDTH])
    plt.ylim([HEIGHT, 0])
    plt.title("sus")
    robiPlot2 = robbi.initSelfPlot()
    pf2 = ParticleFilter()
    pf2.initPlot()

    # 3. subplot
    plt.subplot(223)
    plt.imshow(GRID, cmap="Greys")
    plt.xlim([0, WIDTH])
    plt.ylim([HEIGHT, 0])
    plt.title("rga")
    robiPlot3 = robbi.initSelfPlot()
    pf3 = ParticleFilter()
    pf3.initPlot()

    # 4. subplot
    plt.subplot(224)
    plt.imshow(GRID, cmap="Greys")
    plt.xlim([0, WIDTH])
    plt.ylim([HEIGHT, 0])
    plt.title("hva")
    robiPlot4 = robbi.initSelfPlot()
    pf4 = ParticleFilter()
    pf4.initPlot()


    def mainLoop(i):
        global loopCounter, avgRuntime, maxRuntime
        loopCounter += 1

        # move robot, pf make proposal
        robbi.autoDrive()
        realDist = robbi.measure()

        pf1.moveAll(robbi.motorSignals())
        pf2.moveAll(robbi.motorSignals())
        pf3.moveAll(robbi.motorSignals())
        pf4.moveAll(robbi.motorSignals())

        pf1.measureAll(realDist)
        pf2.measureAll(realDist)
        pf3.measureAll(realDist)
        pf4.measureAll(realDist)

        pf1.autoResample(loopCounter, resampleMethod='rws')
        pf2.autoResample(loopCounter, resampleMethod='sus')
        pf3.autoResample(loopCounter, resampleMethod='rga')
        pf4.autoResample(loopCounter, resampleMethod='hva')

        robbi.updateSelfPlot(robiPlot1)
        robbi.updateSelfPlot(robiPlot2)
        robbi.updateSelfPlot(robiPlot3)
        robbi.updateSelfPlot(robiPlot4)

        pf1.updatePlot()
        pf2.updatePlot()
        pf3.updatePlot()
        pf4.updatePlot()

        if (loopCounter+1) % 300 == 0:
            robbi.moveTo(randomPosition())


    ani = FuncAnimation(fig, mainLoop, interval=TIME_STEP, repeat=True)
    plt.show()
