import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import seaborn as sns
from typing import Final, Union
from scipy.stats import binom

# Binomial distribution default parameters
SAMPLE_SIZE: Final[int] = 100
PFAIL: Final[int] = 0.05

# Overall canvas size
FIG_HEIGHT:Final[float] = 8.0
FIG_WIDTH:Final[float] = 7.0
# Plot position default settings (do not use tight_layout with these)
# These are margins within the figure canvas
LEFT:Final[float] = 0.2
TOP:Final[float] = 0.8
# Padding between subplots
HSPACE:Final[float] = 0.5

# General tolerance value
TOL:Final[float] = 1E-6

class binomial_model:
    """Binomial distribution model class.
    """

    def __init__(self, n: int = SAMPLE_SIZE, pfail: float = PFAIL)->None:
        """Constructor for the binomial distribution model.

        Args:
            n (int, optional): Sample size. Defaults to SAMPLE_SIZE.
            pfail (float, optional): Probability of failure. Defaults to PFAIL.
        """
        self.n = n
        self.pfail = pfail

        self.reset_model()

    def reset_model(self)->None:
        """Regenerates data sets for number of fails, probability density and cumulative probability density.
        """

        # Not sure how many elements to include in each data array so initialise each with the max possible length
        # Set up horizontal axis data of integer number of fails
        self.x_data = np.arange(0, self.n+1)
        # Set up vertical axes data of probability of getting x number of fails
        self.pmf_data = np.empty(len(self.x_data))
        self.cdf_data = np.empty(len(self.x_data))

        for c in np.arange(0, self.n+1):
            # Set horizontal axis point
            self.x_data[c] = c
            # apply prob dens function
            self.pmf_data[c] = binom.pmf(c, self.n, self.pfail)
            # apply cumulative density function
            self.cdf_data[c] = binom.cdf(c, self.n, self.pfail)

            # Break the loop once the CDF gets close enough to its max allowed value of 1.0
            # Try to stop early to make code more responsive
            if self.cdf_data[c] > 1-TOL:
                break

        # Now we know number of elements needed, cut off elements beyond that
        self.x_data = self.x_data[0:c+1]
        self.pmf_data = self.pmf_data[0:c+1]
        self.cdf_data = self.cdf_data[0:c+1]

    def update_pfail(self, pfail:float)->None:
        """Method to update the pfail value.

        Args:
            pfail (float): New value for probability of failure.
        """
        self.pfail = pfail

    def update_n(self, n:int)->None:
        """Method to update the sample size.

        Args:
            n (int): Sample size.
        """
        self.n = n

class binomial_plot:
    """Class to generate plots of binomial distribution functions.
    """

    def __init__(self, model:binomial_model)->None:
        self.model = model

        # Generate canvas
        self.generate_figure()

        # Generate plots
        self.generate_plots()

    def generate_figure(self)->None:
        """Set up the figure canvas including plot axes and input text boxes.
        """
        # Default main plot settings and definitions
        self.fig, ((self.ax0), (self.ax1)) = plt.subplots(2,1)
        self.fig.set_figheight(FIG_HEIGHT)
        self.fig.set_figwidth(FIG_WIDTH)
        self.fig.suptitle("Binomial Distribution", weight="bold")
        self.fig.subplots_adjust(left=LEFT, top=TOP, hspace = HSPACE)

        # Set up user input text boxes
        self.make_pfail_tbox()
        self.make_n_tbox()

    def generate_plots(self)->None:
        """Set up plot axes and generate the plots.
        """

        # Clear the axes so that plots don't drawn on top of each other
        self.ax0.cla()
        self.ax1.cla()

        # Generate plots
        # Note this must be done before setting axis properties, or else will be a mess
        sns.barplot(x=self.model.x_data, y=self.model.pmf_data, ax=self.ax0, color = 'Orange')
        sns.barplot(x=self.model.x_data, y=self.model.cdf_data, ax=self.ax1, color = 'Green')

        # Plot titles
        self.ax0.set_title("Probability Density Function", weight="bold")
        self.ax1.set_title("Cumulative Density Function", weight="bold")        
        
        # Plot axis labels and grid
        self.ax0.set_ylabel("Probability")
        self.ax1.set_ylabel("Cumulative Probability")        
        self.ax0.set_ylim(auto=True)
        self.ax1.set_ylim(top = 1.0)

        for x in [self.ax0, self.ax1]:
            x.set_xlabel("Number Of Fails")
            x.set_xticklabels(x.get_xticklabels(), rotation=45)
            x.grid(visible=True, which='both', axis='y')
            x.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
            x.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
            x.relim()
            x.autoscale_view()
        
        # This is needed to force the plot to refresh or there will be some delay
        self.fig.canvas.draw() 

    def update_data(self)->None:
        """Update the binomial model data and then regenerate plots with new data.
        """
        # Update the model to generate new data
        self.model.reset_model()

        # Update the plots
        self.generate_plots()
        
    def make_pfail_tbox(self)->None:
        """Set up the user input box for probability of failure.
        """
        
        pfail_tbox_ax = self.fig.add_axes([0.3, 0.9, 0.075, 0.04])
        self.pfail_tbox = TextBox(pfail_tbox_ax, "Probability Of Failure", textalignment="left")
        self.pfail_tbox.set_val(f"{PFAIL}")
        # Hook up update method to the event
        self.pfail_tbox.on_submit(self.pfail_update)

    def pfail_update(self, val:Union[str,int])->None:
        """Updates the pfail parameter in the binomial model.

        Args:
            val (Union[str,int]): New pfail value to update.
        """
        
        try:
            pfail = float(val)
        except ValueError:
            print("Invalid probability of failure")
            return
        
        # Prob of failure must be between 0.0 and 1.0
        if pfail > 1.0:
            print("Probability of failure must be less than 1.0")
            return
        elif pfail < 0.0:
            print("Probability of failure must be more than 0.0")
            return

        print(f"New pfail {pfail}")
        self.model.update_pfail(pfail)
        self.update_data()

    def make_n_tbox(self)->None:
        """Set up the user input sample size text box.
        """
        
        pfail_n_ax = self.fig.add_axes([0.6, 0.9, 0.075, 0.04])
        self.n_tbox = TextBox(pfail_n_ax, "Sample Size", textalignment="left")
        self.n_tbox.set_val(f"{SAMPLE_SIZE}")
        # Hook up update method to the event
        self.n_tbox.on_submit(self.n_update)

    def n_update(self, val:Union[str,int])->None:
        """Method to update the sample size variable in the binomial model.

        Args:
            val (Union[str,int]): New value for sample size to update.
        """
        
        try:
            n = int(val)
        except ValueError:
            print("Invalid sample size n")
            return
        
        # Prob of failure must be between 0.0 and 1.0
        if n > 10000:
            print("Sample size must be less than 10000")
            return
        elif n < 1:
            print("Sample size must be more than 0")
            return

        print(f"Sample size {n}")
        self.model.update_n(n)
        self.update_data()        

if __name__ == '__main__':
    # Entry point into main code

    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    print(f"Using backend {matplotlib.get_backend()}")

    # Generate the binomial distribution model and pass it to the plot generator
    m = binomial_model()
    p = binomial_plot(m)
    
    plt.show()