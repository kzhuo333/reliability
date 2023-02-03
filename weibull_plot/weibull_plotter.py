"""Generate plots for Weibull functions.
"""
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from typing import Final, List, Tuple, Union
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
SAMPLE_SIZE:Final[int] = 100
SHAPE_PARAMETER:Final[float] = 1.0
SCALE_PARAMETER:Final[float] = 1.0

class weibull_model:
    def __init__(self, m:float = SHAPE_PARAMETER, c:float = SCALE_PARAMETER, t_count:int = SAMPLE_SIZE, t_start:float = 1E-2, t_end:float = 2.0) -> None:
        self.m = m
        self.c = c
        self.t_data = list(np.linspace(t_start, t_end, t_count))

        self.reset_model()

    def update_m(self, m):
        self.m = m
        self.reset_model()        

    def reset_model(self):
        self.cdf_data = list()
        self.pdf_data = list()
        self.h_data = list()
        for t in self.t_data:
            self.cdf_data.append(wb.cdf(t, self.m, self.c))
            self.pdf_data.append(wb.pdf(t, self.m, self.c))
            self.h_data.append(wb.hazard(t, self.m, self.c))

class weibull_plot:
    def __init__(self, model:weibull_model)->None:
        
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
        self.ax0.set_title("CDF", weight="bold")
        self.ax1.set_title("PDF", weight="bold")
        self.ax2.set_title("Failure Rate", weight="bold")        

        # Plot axis labels and grid
        self.ax0.set_ylabel("Probability (Dimensionless)")
        self.ax1.set_ylabel("Probability Density ($c^{-1}$)")
        self.ax2.set_ylabel("Failure Rate ($c^{-1}$)")
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
        self.note_txt_ax = self.fig.add_axes([0.2, 0.85, 0.075, 0.05])
        self.note_txt_ax.axis("off")
        self.note_txt_ax.text(0.0, 0.0, "$m$ is the shape parameter.\n$c$ is the scale parameter or characteristic lifetime.\nTime $t$ is in multiples of $c$.")

    def make_m_tbox(self)->None:
        
        m_tbox_ax = self.fig.add_axes([0.1, 0.9, 0.075, 0.05])
        self.m_tbox = TextBox(m_tbox_ax, "m", textalignment="left")
        self.m_tbox.set_val(f"{SHAPE_PARAMETER}")
        self.m_tbox_cid = self.m_tbox.on_submit(self.m_update)

    def m_update(self, val:Union[str,int])->None:
        m = float(val)
        print(f"New shape parameter m {m}")
        self.model.update_m(m)

        self.update_data()

    def update_data(self):
        
        self.cdf_line.set_ydata(self.model.cdf_data)
        self.pdf_line.set_ydata(self.model.pdf_data)
        self.h_line.set_ydata(self.model.h_data)

        self.cdf_line.set_xdata(self.model.t_data)        
        self.pdf_line.set_xdata(self.model.t_data)        
        self.h_line.set_xdata(self.model.t_data)

        for x in [self.ax0, self.ax1, self.ax2]:
            x.relim()
            x.autoscale_view()
        
        self.fig.canvas.draw() # This is needed to force the plot to refresh or there will be some delay

if __name__ == "__main__":
    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    print(f"Using backend {matplotlib.get_backend()}")
    
    mm = weibull_model() # Create Weibull model
    pp = weibull_plot(mm) # Pass model into plotter
    
    #plt.tight_layout() # this conflicts with subplots_adjust
    plt.show()
