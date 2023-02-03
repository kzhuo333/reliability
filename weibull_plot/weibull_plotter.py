"""Generate plots for Weibull functions.
"""
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from typing import Final, Union
import numpy as np
import weibull as wb

# Plot position default settings
LEFT:Final[float] = 0.1
TOP:Final[float] = 0.75
WSPACE:Final[float] = 0.2
HSPACE:Final[float] = 0.5
FIG_HEIGHT:Final[float] = 6.0
FIG_WIDTH:Final[float] = 9.0

# Weibull model default settings
SHAPE_PARAMETER:Final[float] = 1.0
SCALE_PARAMETER:Final[float] = 1.0
SAMPLE_SIZE:Final[int] = 100
T_START:Final[float] = 1E-2
T_END:Final[float] = 2.0

class weibull_model:
    """Class to generate Weibull statistics data for given parameters.
    """
    def __init__(self, m:float = SHAPE_PARAMETER, c:float = SCALE_PARAMETER, t_count:int = SAMPLE_SIZE, t_start:float = T_START, t_end:float = T_END) -> None:
        """Constructor requiring shape and scale parameters to generate Weibull model data.

        Args:
            m (float, optional): Shape parameter.
            c (float, optional): Scale parameter.
            t_count (int, optional): No. of points for horizontal axis data.
            t_start (float, optional): Horizontal axis start value.
            t_end (float, optional): Horizontal axis end value.
        """
        self.m = m
        self.c = c
        
        self.t_data = list(np.linspace(t_start, t_end, t_count)) # Generate horizontal axis data

        self.reset_model() # Generate model data

    def update_m(self, m:float)->None:
        """Update the shape parameter.

        Args:
            m (float): Value to update.
        """
        self.m = m
        self.reset_model() # Refresh model data

    def reset_model(self)->None:
        """Regenerate vertical axes data.
        """
        self.cdf_data = list()
        self.pdf_data = list()
        self.h_data = list()
        # Use existing Weibull model parameters to regenerate vertical axis data
        for t in self.t_data:
            self.cdf_data.append(wb.cdf(t, self.m, self.c))
            self.pdf_data.append(wb.pdf(t, self.m, self.c))
            self.h_data.append(wb.hazard(t, self.m, self.c))

class weibull_plot:
    """Class to generate Weibull plots for given Weibull model.
    """
    def __init__(self, model:weibull_model)->None:
        """Constructor requiring Weibull model object.

        Args:
            model (weibull_model): Weibull model object with Weibull parameters and data.
        """
        self.model = model

        # Default main plot settings and definitions
        self.fig, ((self.ax0, self.ax1), (self.ax2, self.ax3)) = plt.subplots(2,2)
        self.fig.set_figheight(FIG_HEIGHT)
        self.fig.set_figwidth(FIG_WIDTH)
        self.fig.suptitle("Weibull Model", weight="bold")
        self.fig.subplots_adjust(left=LEFT, top=TOP, wspace = WSPACE, hspace=HSPACE)
        
        self.ax3.axis("off") # Dummy axis not needed. Blank it.

        # Generate plot lines
        self.cdf_line, = self.ax0.plot(self.model.t_data, self.model.cdf_data, linestyle='solid')
        self.pdf_line, = self.ax1.plot(self.model.t_data, self.model.pdf_data, linestyle='solid')
        self.h_line, = self.ax2.plot(self.model.t_data, self.model.h_data, linestyle='solid')
       
        # Plot titles
        self.ax0.set_title("Cumulative Density Function", weight="bold")
        self.ax1.set_title("Probability Density Function", weight="bold")
        self.ax2.set_title("Failure Rate", weight="bold")        

        # Plot axis labels and grid
        self.ax0.set_ylabel("$F(t)$ (Dimensionless)")
        self.ax1.set_ylabel("$f(t)$ ($c^{-1}$)")
        self.ax2.set_ylabel("$h(t)$ ($c^{-1}$)")
        self.ax0.set_ylim(top = 1.0)
        self.ax1.set_ylim(top = 5.0)
        self.ax2.set_ylim(auto=True)

        for x in [self.ax0, self.ax1, self.ax2]:
            x.set_xlabel("$t$ ($c$)")
            x.grid(visible=True, which='both', axis='both')
        
        # Make textbox for shape parameter m
        self.make_m_tbox()

        # Make textbox for notes
        self.make_note_txt()

        print("Weibull plotter initiated")

    def make_note_txt(self)->None:
        """Method to create non-interactive text box for notes.
        """
        self.note_txt_ax = self.fig.add_axes([0.2, 0.85, 0.075, 0.05])
        self.note_txt_ax.axis("off")
        self.note_txt_ax.text(0.0, 0.0, "$m$ is the shape parameter.\n$c$ is the scale parameter or characteristic lifetime.\nTime $t$ is in multiples of $c$.")

    def make_m_tbox(self)->None:
        """Method to create text box for user to change Weibull shape parameter m.
        """
        m_tbox_ax = self.fig.add_axes([0.1, 0.9, 0.075, 0.05])
        self.m_tbox = TextBox(m_tbox_ax, "m", textalignment="left")
        self.m_tbox.set_val(f"{SHAPE_PARAMETER}")
        # Hook up update method to the event
        self.m_tbox.on_submit(self.m_update)

    def m_update(self, val:Union[str,int])->None:
        """Method to update shape parameter and refresh model data.

        Args:
            val (Union[str,int]): Value to update.
        """
        try:
            m = float(val)
        except ValueError:
            print("Invalid shape parameter")
            return
        
        print(f"New shape parameter m {m}")
        self.model.update_m(m)
        self.update_data()

    def update_data(self)->None:
        """Method to refresh model data.
        """
        self.cdf_line.set_ydata(self.model.cdf_data)
        self.pdf_line.set_ydata(self.model.pdf_data)
        self.h_line.set_ydata(self.model.h_data)

        self.cdf_line.set_xdata(self.model.t_data)        
        self.pdf_line.set_xdata(self.model.t_data)        
        self.h_line.set_xdata(self.model.t_data)

        # Rescale the axes where scaling is set to auto
        for x in [self.ax0, self.ax1, self.ax2]:
            x.relim()
            x.autoscale_view()
        
        self.fig.canvas.draw() # This is needed to force the plot to refresh or there will be some delay

if __name__ == "__main__":
    """Main entry point into Weibull plotter.
    """
    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    print(f"Using backend {matplotlib.get_backend()}")
    
    mm = weibull_model() # Create Weibull model
    pp = weibull_plot(mm) # Pass model into plotter
    
    plt.show()