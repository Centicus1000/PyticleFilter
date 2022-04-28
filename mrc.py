from params import *
from numpy import zeros, tanh, clip
from scopePlot import Scope


# ----------------------------------------------
#           MINIMAL RECURRENT CONTROLLER
#                 23 neuron network
# ----------------------------------------------

class MinimalRecurrentController:

    def __init__(self):
        self.n = zeros(23)  # 23 neurons
        # for debug plotting
        self.osciPlot = None
        self.outputPlot = None

    def step(self, sensor=None):
        # calculate next step of network

        # n_8 is the sensor input
        if sensor is not None:
            self.n[8] = sensor
        newN = zeros(23)  # 23

        # top oscillator
        newN[0] = tanh(OSCI_W11 * self.n[0] + OSCI_W12 * self.n[1] + 0.001)
        newN[1] = tanh(OSCI_W21 * self.n[0] + OSCI_W22 * self.n[1])

        # Conditions
        newN[2] = tanh(-100 * self.n[1])
        newN[3] = tanh(-100 * self.n[1] + 1)
        newN[4] = tanh(+100 * self.n[1] + 1)
        newN[5] = tanh(+100 * self.n[1])
        newN[8] = self.n[8]

        # Left Short Term Memory
        newN[6] = clip(5 * self.n[2] + 5, -1, +1)
        newN[11] = clip(-10 * self.n[6] + self.n[19], -1, +1)
        newN[12] = clip(+10 * self.n[6] + self.n[19], -1, +1)
        # Left Neural Switch
        newN[7] = clip(5 * self.n[3] + 5, -1, +1)
        newN[13] = clip(-10 * self.n[7] + 0.5 * self.n[8] + 10, -1, +1)
        newN[14] = clip(+10 * self.n[7] + 0.5 * self.n[8] - 10, -1, +1)
        # Left Side
        newN[19] = clip(0.5 * self.n[11] + 0.5 * self.n[12] + 0.5 * self.n[13] + 0.5 * self.n[14], -1, +1)

        # Right Neural Switch
        newN[9] = clip(5 * self.n[4] + 5, -1, +1)
        newN[15] = clip(-10 * self.n[9] + 0.5 * self.n[8] + 10, -1, +1)
        newN[16] = clip(+10 * self.n[9] + 0.5 * self.n[8] - 10, -1, +1)
        # Right Short Term Memory
        newN[10] = clip(5 * self.n[5] + 5, -1, +1)
        newN[17] = clip(-10 * self.n[10] + self.n[20], -1, +1)
        newN[18] = clip(+10 * self.n[10] + self.n[20], -1, +1)
        # Right Side
        newN[20] = clip(0.5 * self.n[15] + 0.5 * self.n[16] + 0.5 * self.n[17] + 0.5 * self.n[18], -1, +1)

        # Real MRC -> Motor Signale
        newN[21] = tanh(MRC_W_SELF * self.n[21] + MRC_W_ACROSS * self.n[22] - 18 * self.n[19])
        newN[22] = tanh(MRC_W_SELF * self.n[22] + MRC_W_ACROSS * self.n[21] - 18 * self.n[20])

        self.n = newN

    def motorSignals(self):
        # n21 -> MotorLeft, n22 -> MotorRight
        mL = (1 - MRC_TURN_RATIO) * self.n[21] + MRC_TURN_RATIO * self.n[1]
        mR = (1 - MRC_TURN_RATIO) * self.n[22] - MRC_TURN_RATIO * self.n[1]
        return mL, mR

    # DEBUGGING / PLOTTING

    def topOscillator(self):
        return self.n[0], self.n[1]

    def networkOutput(self):
        return self.n[21], self.n[22]

    def initOsciPlot(self):
        self.osciPlot = Scope(numOfScopes=2, tags=['b-', 'r-'])

    def updateOsciPlot(self):
        self.osciPlot.update(newData=self.n[0:2])

    def initOutputPlot(self):
        self.outputPlot = Scope(numOfScopes=4, tags=['b-', 'r-', 'c:', 'y:'])

    def updateOutputPlot(self):
        mL, mR = self.motorSignals()
        self.outputPlot.update(newData=[self.n[21], self.n[22], mL, mR])

    def debug(self, indices, steps=100):
        # runs certain amount of steps and plots selected neurons
        data = zeros((len(indices), steps))
        sensor = np.sin(2 * np.pi / steps * np.arange(steps))
        for step in range(steps):
            self.step(sensor=sensor[step])
            for (i, j) in enumerate(indices):
                data[i, step] = self.n[j]

        for d in data:
            plt.plot(d)
        plt.show()


if __name__ == '__main__':
    mrc = MinimalRecurrentController()
    mrc.debug([8, 19, 20, 21, 22], steps=200)
