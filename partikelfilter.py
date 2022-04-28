from params import *
from grid import HEIGHT, WIDTH
from patikel import Partikel
from numpy.random import choice, uniform, normal, randint


# ----------------------------------------------
#                PARTIKEL FILTER
# ----------------------------------------------

class PartikelFilter:

    def __init__(self, numOfPartikels=NUM_OF_PARTIKELS, resampleFreq=RESAMPLE_FREQ):
        self.numOfP = numOfPartikels
        self.resFreq = resampleFreq
        self.partikels = np.zeros(self.numOfP, dtype=np.object)
        for i in range(self.numOfP):
            self.partikels[i] = Partikel()
        self.weights = INIT_PARTIKEL_WEIGHT * np.ones(self.numOfP)  # weights of partikel

        self.partikelPlot = None
        self.bestPlot = None
        self.weightPlot = None
        self.averagePlot = None

    # UPDATING PARTIKELS AND WEIGHTS
    def moveAll(self, motorSignals):
        # moving all partikel with given MotorSignals
        # give a PREDICTION
        mL, mR = motorSignals
        for p in self.partikels:
            p.moveBy(mL, mR)

    def measureAll(self, dist):
        # updates weight and confidence of all partikels,
        # according to how well dist fits their own measured dist
        # applies a CORRECTION
        for i, p in enumerate(self.partikels):
            conf = p.confidence(dist)
            if p.isInWall():
                self.weights[i] = 0.0
            else:
                self.weights[i] = STUBBORNNESS * self.weights[i] + (1 - STUBBORNNESS) * conf

    # EVALUATION AND RESAMPLING
    def resampleAll(self):
        for p in self.partikels:
            p.resampleToRandom()
        self.weights = INIT_PARTIKEL_WEIGHT * np.ones(self.numOfP)  # weights of partikel

    def indexOfBest(self):
        return np.argmax(self.weights)

    def indexOfWorst(self):
        return np.argmin(self.weights)

    # ROULETT WHEEL SAMPLING
    def rws(self):
        newPartikels = np.zeros(self.numOfP, dtype=np.object)
        sumOfWeights = np.sum(self.weights)

        for i in range(self.numOfP):
            newPartikels[i] = Partikel()  # neuen Partikel initialisieren

            roulett = uniform(high=sumOfWeights)
            currW = 0
            for j, w in enumerate(self.weights):
                currW += w
                if currW > roulett:
                    newPartikels[i].resampleTo(self.partikels[j])
                    break

        self.partikels = newPartikels
        self.weights = np.average(self.weights) * np.ones(self.numOfP)  # weights of partikel

    # STOCHASTIC UNIVERSAL SAMPLING
    def sus(self):
        newPartikels = np.zeros(self.numOfP, dtype=np.object)
        sumOfWeights = np.sum(self.weights)
        stocStep = sumOfWeights / self.numOfP
        if stocStep < 1E-5:
            self.resampleAll()
        else:
            stochasticArrows = np.arange(start=stocStep * uniform(),
                                         stop=sumOfWeights,
                                         step=stocStep)
            currI = 0
            currW = self.weights[currI]
            for i, arrow in enumerate(stochasticArrows):
                newPartikels[i] = Partikel()
                while currW < arrow:
                    currI += 1
                    currW += self.weights[currI]
                newPartikels[i].resampleTo(self.partikels[currI])

            self.partikels = newPartikels
            self.weights = np.average(self.weights) * np.ones(self.numOfP)

    def rga(self):
        REC = 0.5  # recombination
        MUT = 0.5  # mutaion

        avg = np.average(self.weights)

        for i in range(self.resFreq):
            winIdx = randint(self.numOfP)
            losIdx = self.indexOfWorst()

            winner = self.partikels[winIdx]
            loser = self.partikels[losIdx]

            if uniform() <= REC:
                loser.x = winner.x
            if uniform() <= REC:
                loser.y = winner.y
            if uniform() <= REC:
                loser.phi = winner.phi
            if uniform() <= MUT:
                loser.x = normal(loser.x, WIDTH * RESAMPLE_NOISE)
            if uniform() <= MUT:
                loser.y = normal(loser.y, HEIGHT * RESAMPLE_NOISE)
            if uniform() <= MUT:
                loser.phi = normal(loser.phi, 2 * np.pi * RESAMPLE_NOISE)
            loser.fixPosition()
            self.weights[losIdx] = avg

    # HENRIK AND VINCENTS APPROACH
    def hva(self):
        bestI = self.indexOfBest()
        bestW, bestP = self.weights[bestI], self.partikels[bestI]

        averageWeight = np.average(self.weights)

        for i in range(self.resFreq):
            worstI = self.indexOfWorst()  # finde den schlechtesten Partikel
            worstP = self.partikels[worstI]
            self.weights[worstI] = averageWeight  # gib partikel noch eine chance, gewischt wird average

            # resampling state machine
            if bestW > GOOD_THEORY_THRESH and choice([True, False]):
                # GOOD -> moves partikels closer
                worstP.resampleTo(bestP)
            else:
                # BAD -> scatters partikels to random locations
                worstP.resampleToRandom()

    def autoResample(self, loopCounter, resampleMethod=RESAMPLE_METHOD):
        if resampleMethod == 'rga':
            self.rga()
        elif resampleMethod == 'hva':
            self.hva()
        elif loopCounter % int(self.numOfP/self.resFreq) == 0:
            if resampleMethod == 'rws':
                self.rws()
            elif resampleMethod == 'sus':
                self.sus()

    # PLOTTING
    def allCoords(self):
        # returns x and y's of all Partikel for plotting
        pos = np.zeros((self.numOfP, 2))
        for i, p in enumerate(self.partikels):
            pos[i, :] = p.coords()
        return pos

    def initPlot(self):
        pfCoords = self.allCoords()
        bestCoords = self.partikels[self.indexOfBest()].coords()
        self.partikelPlot = plt.scatter(pfCoords[:, 0], pfCoords[:, 1], s=self.weights)
        self.bestPlot, = plt.plot(bestCoords[0], bestCoords[1], 'r*')

    def initWeightPlot(self):
        self.weightPlot, = plt.plot(self.weights, 'bo')
        plt.xlim([0, self.numOfP])
        plt.ylim([0, 1])
        plt.plot([0, self.numOfP], [GOOD_THEORY_THRESH, GOOD_THEORY_THRESH], 'r:')
        self.averagePlot, = plt.plot([0, self.numOfP], [0.5, 0.5], 'g--')

    def updatePlot(self):
        pfSizes = self.weights * PARTIKEL_SIZE_FAK
        pfCoords = self.allCoords()
        bestCoords = self.partikels[self.indexOfBest()].coords()
        self.partikelPlot.set_offsets(np.c_[pfCoords[:, 0], pfCoords[:, 1]])
        self.partikelPlot.set_sizes(pfSizes)
        self.bestPlot.set_data(bestCoords[0], bestCoords[1])
        if self.weightPlot is not None:
            self.weightPlot.set_ydata(self.weights)
            average = np.average(self.weights)
            self.averagePlot.set_ydata([average, average])
