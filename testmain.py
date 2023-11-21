from grid import *
from particlefilter import ParticleFilter
from robot import Robot
from time import perf_counter as currentTime

# ----------------------------------------------
#                TESTING RESAMPLING
# ----------------------------------------------

if __name__ == '__main__':

    # resampl methods:
    #   rws = roulett wheel sampling
    #   sus = stochastic universal sampling
    #   rga = resampling genetic approach
    #   hva = henrik & vincent approach
    AVG_W_QUITTHRESH = 0.9
    resampleFreq = 10

    for resampleMethod in ['rws', 'sus', 'rga', 'hva']:
        for resampleFreq in np.linspace(50, 400, 40, dtype=np.int):
            loopCounter = 0
            timeCounter = 0.0
            resampleInterval = int(NUM_OF_PARTIKELS/resampleFreq)
            # echten roboter erstellen
            robbi = Robot()
            robbi.initSelfPlot()

            # Partikel filter erstellen
            pf = ParticleFilter(NUM_OF_PARTIKELS, resampleFreq)
            pf.initPlot()

            # main loop
            while loopCounter < 1000:
                loopCounter += 1

                # move robot, pf make proposal
                robbi.autoDrive()
                pf.moveAll(robbi.motorSignals())
                # robot measures, pf makes correction
                realDist = robbi.measure()
                pf.measureAll(realDist)

                tic = currentTime()
                pf.autoResample(loopCounter)
                tac = currentTime()
                timeCounter += (tac - tic)

                if np.average(pf.weights) > AVG_W_QUITTHRESH:
                    break

            avgRuntime = timeCounter/loopCounter
            print(resampleMethod, resampleFreq, loopCounter, avgRuntime)