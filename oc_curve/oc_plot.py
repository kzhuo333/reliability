#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plotter for operating characteristic curve.

Created on Tue Dec 13 02:38:54 2022

@author: kzhuo
"""


import sys
sys.path.insert(0, '/Users/kzhuo/kz/oc_curve')

from oc_curve import get_envelope, oc_curve
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from typing import Final, List, Tuple

import matplotlib
%matplotlib auto

# Positions of plot components, as fraction of canvas size
X_CORNER:Final[float] = 0.25 # main plot x corner
Y_CORNER:Final[float] = 0.3 # main plot y corner
SLIDER_WIDTH:Final[float] = 0.02
SLIDER_LENGTH:Final[float] = 0.6
SLIDER_OFFSET:Final[float] = 0.15 # slider offset from the main plot

# Sample plan defaults
SAMPLE_SIZE:Final[int] = 300
ACCEPTANCE_NUMBER:Final[int] = 3
ALPHA:Final[float] = 0.05
BETA:Final[float] = 0.10

class oc_plotter:
    """
    Plotter class for operating characteristic curve. 
    """
    
    def __init__(self, x_data:List[float], y_data:List[float])->None:
        """
        Operating characteristic curve plotter constructor.

        Parameters
        ----------
        x_data : List[float]
            OC x data i.e. the pfail aka non-conformity aka failure rate.
        y_data : List[float]
            OC y data i.e. the prob of lot acceptance.

        Returns
        -------
        None
        """
        # Set the main x and y data
        self.x_data = x_data
        self.y_data = y_data

        # Default plot settings and definitions
        self.fig, self.ax = plt.subplots()
        self.fig.set_figheight(6)
        self.fig.set_figwidth(12)
        self.ax.set_title(f"OC Curve (n={SAMPLE_SIZE}, k={ACCEPTANCE_NUMBER})")
        self.ax.set_ylabel("Probability of Acceptance")
        self.ax.set_xlabel("Lot Probability Defective")
        self.ax.set_ylim(ymax = 1.0, ymin = 0.0)
        self.ax.set_xlim(xmax = 0.1, xmin = 0.0)
        self.ax.grid(visible=True, which='both', axis='both')
        
        # Add in the main OC curve, along with AQL and RQL points
        self.fig.subplots_adjust(left=X_CORNER, bottom=Y_CORNER)
        self.line, = self.ax.plot(self.x_data, self.y_data, linestyle='dashed', marker='x') # The OC line object
        # Define these placeholders with dummy values to enable update at end
        self.aql_pt, = self.ax.plot([0.0, 0.0],[0.0, 0.0], marker='o', color='g', markersize=8) # The aql point object (as a line)
        self.rql_pt, = self.ax.plot([0.0, 0.0],[0.0, 0.0], marker='o', color='r', markersize=8) # The rql point object (as a line)
        self.aql_anno = self.ax.annotate("AQL", (0.0, 0.0)) # The aql point annotation
        self.rql_anno = self.ax.annotate("RQL", (0.0, 0.0)) # The rql point annotation
        
        # Make axes sliders
        self.make_ylim_slider()
        self.make_xlim_slider()
        
        # Make sample plan parameter text boxes
        self.make_sample_size_tbox()
        self.make_acceptance_number_tbox()
        
        # Make Alpha risk and AQL text boxes
        self.make_alpha_tbox()
        self.make_aql_tbox()      
        # Update Alpha and AQL to default values
        self.alpha_update(f"{ALPHA}")
        
        # Make Beta risk and RQL text boxes
        self.make_beta_tbox()
        self.make_rql_tbox()
        # UPdate Beta and RQL to default values
        self.beta_update(f"{BETA}")
        
        print("OC plotter initiated")
        

    #%% Generic data update methods
    def update_data(self, x_data:List[float], y_data:List[float])->None:
        """
        Reset x and y data then redraw the plot.

        Parameters
        ----------
        x_data : List[float]
            New x data to update.
        y_data : List[float]
            New y data to update.

        Returns
        -------
        None.

        """
        
        self.x_data = x_data
        self.y_data = y_data
        self.line.set_ydata(y_data)
        self.line.set_xdata(x_data)
        self.ax.relim()
        self.fig.canvas.draw() # This is needed to force the plot to refresh or there will be some delay
        print("Plot data updated")
        
        # Update the Alpha and Beta (along with AQL and RQL implicitly)
        self.alpha_update(self.alpha_tbox.text)
        self.beta_update(self.beta_tbox.text)
        
        
    def get_line(self, idx_l:int, idx_r:int)->Tuple[float, float]:
        """
        Calculate gradient and y-intercept between 2 points of data.

        Parameters
        ----------
        idx_l : int
            The left data point index.
        idx_r : int
            The right data point index.

        Returns
        -------
        Tuple[float, float]
            Tuple of gradient and y-intercept.

        """
        
        xl = self.x_data[idx_l]
        xr = self.x_data[idx_r]
        yl = self.y_data[idx_l]
        yr = self.y_data[idx_r]
        m = (yr-yl) / (xr-xl) # Gradient
        c = yl - m*xl # y-intercept
        return m, c
    
    def update_aql_pt(self, x_target:float, y_target:float)->None:
        """
        Update the AQL point and annotation.

        Parameters
        ----------
        x_target : float
            AQL x coord.
        y_target : float
            AQL y coord.

        Returns
        -------
        None

        """
        
        self.aql_pt.set_xdata([x_target])
        self.aql_pt.set_ydata([y_target])
        self.aql_anno.remove()
        self.aql_anno = self.ax.annotate("-> AQL", (x_target, y_target), weight='bold', fontsize=12)
        self.ax.relim()
        self.fig.canvas.draw() # This is needed to force the plot to refresh or there will be some delay
    
    def update_rql_pt(self, x_target:float, y_target:float)->None:
        """
        Update the rql point and annotation.

        Parameters
        ----------
        x_target : float
            rql x coord.
        y_target : float
            rql y coord.

        Returns
        -------
        None

        """
        
        self.rql_pt.set_xdata([x_target])
        self.rql_pt.set_ydata([y_target])
        self.rql_anno.remove()
        self.rql_anno = self.ax.annotate("-> RQL", (x_target, y_target), weight='bold', fontsize=12)
        self.ax.relim()
        self.fig.canvas.draw() # This is needed to force the plot to refresh or there will be some delay

    #%% ylim slider
    def make_ylim_slider(self)->None:
        """
        Make slider widget to adjust y range

        Returns
        -------
        None
            DESCRIPTION.
        """
        # Make a vertically oriented slider to control the probability of acceptance
        ylim_slider_ax = self.fig.add_axes([X_CORNER-SLIDER_OFFSET, Y_CORNER, SLIDER_WIDTH, SLIDER_LENGTH]) #https://matplotlib.org/stable/api/figure_api.html
        self.ylim_slider = Slider(
            ax = ylim_slider_ax,
            label="ylim",
            valmin=0.001,
            valmax=1,
            valinit=1,
            orientation="vertical"
        )
        self.ylim_slider.on_changed(self.ylim_update)
    
    def ylim_update(self, val):
        self.ax.set_ylim(0.0, self.ylim_slider.val)
        self.fig.canvas.draw_idle()
        
    #%% xlim slider
    def make_xlim_slider(self)->None:
        """
        Make a horizontally oriented slider to control the probability of lot non-conformance.

        Returns
        -------
        None
        """
        xlim_slider_ax = self.fig.add_axes([X_CORNER, Y_CORNER-SLIDER_OFFSET, SLIDER_LENGTH, SLIDER_WIDTH]) #https://matplotlib.org/stable/api/figure_api.html
        self.xlim_slider = Slider(
            ax = xlim_slider_ax,
            label="xlim",
            valmin=0.001,
            valmax=1,
            valinit=0.1,
            orientation="horizontal"
        )
        
        # Link the slider to update function
        self.xlim_slider.on_changed(self.xlim_update)
        
    def xlim_update(self, val)->None:
        """
        Method to set x range limit. To connect to x range slider widget.

        Parameters
        ----------
        val : TYPE
            Limit for x range.

        Returns
        -------
        None

        """
        self.ax.set_xlim(0.0, self.xlim_slider.val)
        self.fig.canvas.draw_idle()
    
    #%% Sample size text box
    def make_sample_size_tbox(self)->None:
        """
        Makes text box widget for sample size entry.

        Returns
        -------
        None
            DESCRIPTION.

        """
        sample_size_tbox_ax = self.fig.add_axes([0.1, 0.05, 0.075, 0.05])
        self.sample_size_tbox = TextBox(sample_size_tbox_ax, "n", textalignment="left")
        self.sample_size_tbox.set_val(f"{SAMPLE_SIZE}")
    
    #%% Acceptance number text box
    def make_acceptance_number_tbox(self)->None:
        """
        Make text box widget for acceptance number entry.

        Returns
        -------
        None
            DESCRIPTION.

        """
        acceptance_number_tbox_ax = self.fig.add_axes([0.2, 0.05, 0.075, 0.05])
        self.acceptance_number_tbox = TextBox(acceptance_number_tbox_ax, "k", textalignment="left")
        self.acceptance_number_tbox.set_val(f"{ACCEPTANCE_NUMBER}")
        
    #%% Alpha
    def make_alpha_tbox(self)->None:
        """
        Make text box widget for alpha risk entry.

        Returns
        -------
        None
            DESCRIPTION.

        """
        alpha_tbox_ax = self.fig.add_axes([0.4, 0.05, 0.075, 0.05])
        self.alpha_tbox = TextBox(alpha_tbox_ax, "Alpha", textalignment="left")
        self.alpha_tbox.set_val(f"{ALPHA}")
        self.alpha_tbox_cid = self.alpha_tbox.on_submit(self.alpha_update) # Note cid to connect/disconnect events
        
    
    def alpha_update(self, val:str)->None:
        """
        Update method for Alpha risk textbox. Updates (1) AQL textbox and (2) point for given Alpha.

        Parameters
        ----------
        val : string
            Alpha update string from UI.

        Returns
        -------
        None
        """
        
        # Use linear interpolation to find AQL target corresponding to given Alpha target
        y_target = 1.0 - float(val)
        print(f"New Alpha {y_target}")
        idx_l, idx_r = get_envelope(self.y_data, y_target)
        m, c = self.get_line(idx_l, idx_r)
        x_target = (y_target - c) / m
        #x_target = round(x_target, 3)
        
        # Update the AQL textbox
        self.aql_tbox.disconnect(self.aql_tbox_cid) # Disconnect update event
        self.aql_tbox.set_val("{0:.3f}".format(x_target))
        self.aql_tbox_cid = self.aql_tbox.on_submit(self.aql_update) # Reconnect update event
        
        self.update_aql_pt(x_target, y_target)
        
    
    #%% AQL
    def make_aql_tbox(self)->None:
        """
        Make text box widget for AQL entry.

        Returns
        -------
        None
            DESCRIPTION.

        """
        aql_tbox_ax = self.fig.add_axes([0.53, 0.05, 0.075, 0.05])
        self.aql_tbox = TextBox(aql_tbox_ax, "AQL", textalignment="left")
        self.aql_tbox_cid = self.aql_tbox.on_submit(self.aql_update) # Note cid to connect/disconnect events
        
    def aql_update(self, val:str)->None:
        """
        Method to update AQL.

        Parameters
        ----------
        val : str
            Value to update AQL.

        Returns
        -------
        None
            DESCRIPTION.

        """
        # Use linear interpolation to find Alpha target corresponding to given AQL target
        x_target = float(val)
        print(f"New AQL {x_target}")
        idx_l, idx_r = get_envelope(self.x_data, x_target)
        m, c = self.get_line(idx_l, idx_r)
        y_target = m * x_target + c
        y_target = round(y_target, 3)
        
        # Update the Alpha textbox
        self.alpha_tbox.disconnect(self.alpha_tbox_cid) # Disconnect update event
        self.alpha_tbox.set_val("{0:.3f}".format(1.0 - y_target))
        self.alpha_tbox_cid = self.alpha_tbox.on_submit(self.alpha_update) # Reconnect update event
        
        self.update_aql_pt(x_target, y_target)

    #%% Beta
    def make_beta_tbox(self)->None:
        """
        Make text box widget for Beta risk entry.

        Returns
        -------
        None
            DESCRIPTION.

        """
        beta_tbox_ax = self.fig.add_axes([0.7, 0.05, 0.075, 0.05])
        self.beta_tbox = TextBox(beta_tbox_ax, "Beta", textalignment="left")
        self.beta_tbox.set_val(f"{BETA}")
        self.beta_tbox_cid = self.beta_tbox.on_submit(self.beta_update)
    
    def beta_update(self, val:str)->None:
        """
        Update method for beta risk textbox. Updates (1) rql textbox and (2) point for given beta.

        Parameters
        ----------
        val : string
            beta update string from UI.

        Returns
        -------
        None
        """
        
        # Use linear interpolation to find rql target corresponding to given beta target
        y_target = float(val)
        print(f"New beta {y_target}")
        idx_l, idx_r = get_envelope(self.y_data, y_target)
        m, c = self.get_line(idx_l, idx_r)
        x_target = (y_target - c) / m
        #x_target = round(x_target, 3)
        
        # Update the rql textbox
        self.rql_tbox.disconnect(self.rql_tbox_cid) # Disconnect update event
        self.rql_tbox.set_val("{0:.3f}".format(x_target))
        self.rql_tbox_cid = self.rql_tbox.on_submit(self.rql_update) # Reconnect update event
        
        self.update_rql_pt(x_target, y_target)
        
    #%% RQL
    def make_rql_tbox(self):
        """
        Make text box widget for RQL entry.

        Returns
        -------
        None.

        """
        rql_tbox_ax = self.fig.add_axes([0.83, 0.05, 0.075, 0.05])
        self.rql_tbox = TextBox(rql_tbox_ax, "RQL", textalignment="left")
        self.rql_tbox_cid = self.rql_tbox.on_submit(self.rql_update)
        
    def rql_update(self, val:str)->None:
        """
        Method to update RQL.

        Parameters
        ----------
        val : str
            Value to update RQL.

        Returns
        -------
        None
            DESCRIPTION.

        """
        x_target = float(val)
        print(f"New rql {x_target}")
        idx_l, idx_r = get_envelope(self.x_data, x_target)
        m, c = self.get_line(idx_l, idx_r)
        y_target = m * x_target + c
        #y_target = round(y_target, 3)
        
        # Update the Beta textbox
        self.beta_tbox.disconnect(self.beta_tbox_cid) # Disconnect update event
        self.beta_tbox.set_val("{0:.3f}".format(y_target))
        self.beta_tbox_cid = self.beta_tbox.on_submit(self.beta_update) # Reconnect update event
        
        self.update_rql_pt(x_target, y_target)
        
if __name__ == "__main__":
    # Set the matplotlib plotting backend
    backend = matplotlib.get_backend()
    if backend != 'Qt5Agg':
        matplotlib.use("Qt5Agg") # macosx backend is buggy for textbox widget. qt5 seems decent.
    
    print(f"Using backend {matplotlib.get_backend()}")
    
    #%% Set up default OC plot
    oc = oc_curve(SAMPLE_SIZE, ACCEPTANCE_NUMBER, ALPHA, BETA)   
    plotter = oc_plotter(oc.x_data, oc.y_data)
    
    #%% Sample size updater. Interfaces between plotter and oc.
    def sample_size_update(sample_size:int)->None:
        ss = int(sample_size)
        print(f"New sample size {ss}")
        oc.update_sample_size(ss)
        plotter.ax.set_title(f"OC Curve (n={oc.sample_size}, k={oc.n_accept})")
        plotter.update_data(oc.x_data, oc.y_data)
        
    #%% Acceptance number updater. Interfaces between plotter and oc.
    def acceptance_number_update(acceptance_number:int)->None:
        n_accept = int(acceptance_number)
        print(f"New acceptance number {n_accept}")
        oc.update_acceptance_number(n_accept)
        plotter.ax.set_title(f"OC Curve (n={oc.sample_size}, k={oc.n_accept})")
        plotter.update_data(oc.x_data, oc.y_data)
    
    # Hook up sample plan parameter text box events
    plotter.acceptance_number_tbox.on_submit(acceptance_number_update)
    plotter.sample_size_tbox.on_submit(sample_size_update)
    
    plt.show()