"""Generate plots for Weibull functions.
"""
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from typing import Final, List, Tuple, Union
import numpy as np

import weibull as wb

print('hello world')
SAMPLE_SIZE:Final = 100

class weibull_model:
    def __init__(self, m:float = 1.0, c:float = 1.0, t_count:int = SAMPLE_SIZE, t_start:float = 0.0, t_end:float = 2.0) -> None:
        self.m = m
        self.c = c
        self.t_data = list(np.linspace(t_start, t_end, t_count))

        self.cdf_data = list()
        self.pdf_data = list()
        self.h_data = list()
        for t in self.t_data:
            self.cdf_data.append(wb.cdf(t, self.m, self.c))
            self.pdf_data.append(wb.pdf(t, self.m, self.c))
            self.h_data.append(wb.hazard(t, self.m, self.c))

class weibull_plot:
    def __init__(self, model:weibull_model)->None:
        
        self.model = weibull_model()

        # Default plot settings and definitions
        self.fig, (self.ax0, self.ax1, self.ax2) = plt.subplots(3)
        self.fig.set_figheight(6)
        self.fig.set_figwidth(12)
        self.fig.suptitle("Weibull Model")

        self.cdf_line, = self.ax0.plot(self.model.t_data, self.model.cdf_data, linestyle='dashed', marker='x')
        self.pdf_line, = self.ax1.plot(self.model.t_data, self.model.pdf_data, linestyle='dashed', marker='x')
        self.h_line, = self.ax2.plot(self.model.t_data, self.model.h_data, linestyle='dashed', marker='x')

        print("Weibull plotter initiated")

if __name__ == "__main__":
    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    
    print(f"Using backend {matplotlib.get_backend()}")
    
    m = weibull_model(10)
    w = weibull_plot(m)
    
    plt.show()
# %%
