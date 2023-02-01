"""Generate plots for Weibull functions.
"""
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from typing import Final, List, Tuple, Union


import weibull

print('hello world')
print(weibull.cdf(1.0, 1.0, 1.0))

if __name__ == "__main__":
    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    
    print(f"Using backend {matplotlib.get_backend()}")
    
    
    plt.show()
# %%
