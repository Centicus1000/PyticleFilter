from params import *
from matplotlib.animation import FuncAnimation


# ----------------------------------------------
#              PLOT FOR SCOPING
# ----------------------------------------------

class Scope:

    def __init__(self, numOfScopes, tags):
        self.numOfScopes = numOfScopes
        self.data = np.zeros((numOfScopes, 50))
        self.plots = []
        for i in range(numOfScopes):
            plot, = plt.plot(self.data[i], tags[i])
            self.plots.append(plot)

    def update(self, newData):
        if self.numOfScopes == 1:
            self.data[0] = np.roll(self.data[0], -1)
            self.data[0, -1] = newData
            self.plots[0].set_ydata(self.data[0])
        else:
            for i in range(self.numOfScopes):
                self.data[i] = np.roll(self.data[i], -1)
                self.data[i, -1] = newData[i]
                self.plots[i].set_ydata(self.data[i])


# debug
if __name__ == '__main__':
    fig = plt.figure(figsize=(15, 10))
    s = Scope(numOfScopes=1, tags=['r-'])
    plt.ylim([-1, 1])


    def update(i):
        rand = np.random.ranf()
        print(s.data, rand)
        s.update(rand)


    ani = FuncAnimation(fig, update, frames=100, interval=100, repeat=True)
    plt.show()
