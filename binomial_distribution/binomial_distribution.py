import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Final
from scipy.stats import binom

# Binomial distribution default parameters
SAMPLE_SIZE: Final[int] = 1000
PFAIL: Final[int] = 0.01

# Plot position default settings
LEFT:Final[float] = 0.1
TOP:Final[float] = 0.75
WSPACE:Final[float] = 0.2
HSPACE:Final[float] = 0.5
FIG_HEIGHT:Final[float] = 6.0
FIG_WIDTH:Final[float] = 9.0

class binomial_model:
    def __init__(self, n: int = SAMPLE_SIZE, pfail: float = PFAIL)->None:
        self.n = n
        self.pfail = pfail

        self.reset_model()

    def reset_model(self)->None:
        # Set up horizontal axis data of integer number of fails
        self.x_data = np.arange(0, self.n+1)

        # Set up vertical axes data of probability of getting x number of fails
        self.pmf_data = np.empty(len(self.x_data))
        self.cdf_data = np.empty(len(self.x_data))
        for i, c in enumerate(self.x_data):
            # apply prob dens function
            self.pmf_data[i] = binom.pmf(c, self.n, self.pfail)
            # apply cumulative density function
            self.cdf_data[i] = binom.cdf(c, self.n, self.pfail)

class binomial_plot:
    def __init__(self, model:binomial_model)->None:
        self.model = model

        # Default main plot settings and definitions
        self.fig, (self.ax0, self.ax1) = plt.subplots(1,2)
        self.fig.set_figheight(FIG_HEIGHT)
        self.fig.set_figwidth(FIG_WIDTH)
        self.fig.suptitle("Binomial Distribution", weight="bold")
        self.fig.subplots_adjust(left=LEFT, top=TOP, wspace = WSPACE, hspace=HSPACE)

        # Generate plots
        # Note this must be done before setting axis properties, or else will be a mess
        sns.barplot(x=self.model.x_data, y=self.model.pmf_data, ax=self.ax0, color = 'Orange')
        sns.barplot(x=self.model.x_data, y=self.model.cdf_data, ax=self.ax1, color = 'Green')

        # Plot titles
        self.ax0.set_title("Probability Density Function", weight="bold")
        self.ax1.set_title("Cumulative Density Function", weight="bold")
        
        # Plot axis labels and grid
        self.ax0.set_ylabel("Probability Density")
        self.ax1.set_ylabel("Cumulative Probability Density")        
        self.ax0.set_ylim(auto=True)
        self.ax1.set_ylim(top = 1.0)

        
        xlim = self.get_xlim()
        for x in [self.ax0, self.ax1]:
            x.set_xlim(left = 0.0, right = xlim)
            x.set_xlabel("Number Of Fails")
            x.grid(visible=True, which='both', axis='both')


    def get_xlim(self):
        default_index = len(self.model.cdf_data) - 1 
        idx = next((i for i, xx in enumerate(self.model.cdf_data) if xx > 1-1E-9), default_index)
        return self.model.x_data[idx]

if __name__ == '__main__':
    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    print(f"Using backend {matplotlib.get_backend()}")

    m = binomial_model()
    p = binomial_plot(m)

    plt.tight_layout()
    plt.show()