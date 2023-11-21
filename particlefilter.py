from params import *
from grid import HEIGHT, WIDTH
from patikel import Partikel
from numpy.random import choice, uniform, normal, randint


# ----------------------------------------------
#                PARTICLE FILTER
# ----------------------------------------------

class ParticleFilter:

    def __init__(self, nParticles=NUM_OF_PARTIKELS, resampleFreq=RESAMPLE_FREQ):
        self.numOfP = nParticles
        self.resFreq = resampleFreq
        self.particles = np.zeros(self.numOfP, dtype=object)
        for i in range(self.numOfP):
            self.particles[i] = Partikel()
        self.weights = INIT_PARTIKEL_WEIGHT * np.ones(self.numOfP)  # weights of particle

        self.particlePlot = None
        self.bestPlot = None
        self.weightPlot = None
        self.averagePlot = None

    # UPDATING PARTICLES AND WEIGHTS
    def moveAll(self, motorSignals):
        # moving all particle with given MotorSignals
        # give a PREDICTION
        mL, mR = motorSignals
        for p in self.particles:
            p.moveBy(mL, mR)

    def measureAll(self, dist):
        # updates weight and confidence of all particles,
        # according to how well dist fits their own measured dist
        # applies a CORRECTION
        for i, p in enumerate(self.particles):
            conf = p.confidence(dist)
            if p.isInWall():
                self.weights[i] = 0.0
            else:
                self.weights[i] = STUBBORNNESS * self.weights[i] + (1 - STUBBORNNESS) * conf

    # EVALUATION AND RESAMPLING
    def resampleAll(self):
        for p in self.particles:
            p.resampleToRandom()
        self.weights = INIT_PARTIKEL_WEIGHT * np.ones(self.numOfP)  # weights of particle

    def indexOfBest(self):
        return np.argmax(self.weights)

    def indexOfWorst(self):
        return np.argmin(self.weights)

    # ROULETTE WHEEL SAMPLING
    def rws(self):
        newParticles = np.zeros(self.numOfP, dtype=np.object)
        sumOfWeights = np.sum(self.weights)

        for i in range(self.numOfP):
            newParticles[i] = Partikel()  # initialise a new particle

            roulette = uniform(high=sumOfWeights)
            currW = 0
            for j, w in enumerate(self.weights):
                currW += w
                if currW > roulette:
                    newParticles[i].resampleTo(self.particles[j])
                    break

        self.particles = newParticles
        self.weights = np.average(self.weights) * np.ones(self.numOfP)  # weights of particle

    # STOCHASTIC UNIVERSAL SAMPLING
    def sus(self):
        newParticles = np.zeros(self.numOfP, dtype=np.object)
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
                newParticles[i] = Partikel()
                while currW < arrow:
                    currI += 1
                    currW += self.weights[currI]
                newParticles[i].resampleTo(self.particles[currI])

            self.particles = newParticles
            self.weights = np.average(self.weights) * np.ones(self.numOfP)

    def rga(self):
        REC = 0.5  # recombination
        MUT = 0.5  # mutation

        avg = np.average(self.weights)

        for i in range(self.resFreq):
            winIdx = randint(self.numOfP)
            losIdx = self.indexOfWorst()

            winner = self.particles[winIdx]
            loser = self.particles[losIdx]

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
        bestW, bestP = self.weights[bestI], self.particles[bestI]

        averageWeight = np.average(self.weights)

        for i in range(self.resFreq):
            worstI = self.indexOfWorst()  # find the worst particle
            worstP = self.particles[worstI]
            # give the particle another chance, by setting it to the current average weight
            self.weights[worstI] = averageWeight

            # resampling state machine
            if bestW > GOOD_THEORY_THRESH and choice([True, False]):
                # GOOD -> moves particles closer
                worstP.resampleTo(bestP)
            else:
                # BAD -> scatters particles to random locations
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
        # returns x and y's of all particles for plotting
        pos = np.zeros((self.numOfP, 2))
        for i, p in enumerate(self.particles):
            pos[i, :] = p.coords()
        return pos

    def initPlot(self):
        pfCoords = self.allCoords()
        bestCoords = self.particles[self.indexOfBest()].coords()
        self.particlePlot = plt.scatter(pfCoords[:, 0], pfCoords[:, 1], s=self.weights)
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
        bestCoords = self.particles[self.indexOfBest()].coords()
        self.particlePlot.set_offsets(np.c_[pfCoords[:, 0], pfCoords[:, 1]])
        self.particlePlot.set_sizes(pfSizes)
        self.bestPlot.set_data(bestCoords[0], bestCoords[1])
        if self.weightPlot is not None:
            self.weightPlot.set_ydata(self.weights)
            average = np.average(self.weights)
            self.averagePlot.set_ydata([average, average])
