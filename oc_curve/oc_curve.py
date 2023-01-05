from scipy.stats import binom
import numpy as np
from typing import List, Tuple

def get_oc(k:int, n:int, p_end:float=0.20, p_step:float=0.01)->Tuple[List[float], List[float]]:
    """
    Generate operating characteristic curve data for a given sample size n.

    Parameters
    ----------
    k : int
        Acceptance number.
    n : int
        Sample size.
    p_end : float, optional
        Max value for percent defective range. The default is 0.20.
    p_step : float, optional
        Step size for percent defective range. The default is 0.01.

    Returns
    -------
    (Tuple[List[float], List[float]])
        Prob accept vs lot defectivity.

    """
    
    x = list(np.arange(0.0, p_end, p_step))
    y = []
    for pp in x:
        # Cumulative sum of probability acceptance for fails <= acceptance number
        p_accept_cum = 0.0
        for kk in list(range(0,k+1)):
            p_accept_cum = p_accept_cum + binom.pmf(kk, n, pp)
        y.append(p_accept_cum)
    return x, y
    
def get_envelope(x:List[float], target:float)->Tuple[int, int]:
    """
    Method to find (1) left and (2) right values in data list which envelope given target.

    Parameters
    ----------
    x : List[float]
        Input data to find envelope from.
    target : float
        Target value to find envelope over.

    Returns
    -------
    Tuple[int, int]
        Left and right data values which envelope the target.

    """
    
    d = [(idx, abs(target-xx)) for idx, xx in enumerate(x)]
    d.sort(key = lambda xx: xx[1])
    return d[0][0], d[1][0]

class oc_curve:
    def __init__(self, sample_size:int = 300, acceptance_number:int= 3, alpha:float = 0.05, beta:float = 0.10)->None:
        """
        Constructor for oc_curve object. Given sample plan parameters, will generate data for an operating characteristic curve.

        Parameters
        ----------
        sample_size : int, optional
            Sample size value for binomial cdf. The default is 300.
        acceptance_number : int, optional
            Acceptance number value for binomial cdf. The default is 3.
        alpha : float, optional
            Alpha producer risk. The default is 0.05.
        beta : float, optional
            Beta customer risk. The default is 0.10.

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.sample_size = sample_size
        self.n_accept = acceptance_number
        self.alpha = alpha
        self.beta = beta
        self.make_data()
    
    def make_data(self, p_end:float=0.20, p_step:float=0.001)->None:
        """
        Method to generate data for the OC curve.

        Parameters
        ----------
        p_end : float, optional
            Ending step value for the pfail (x-axis). The default is 0.20.
        p_step : float, optional
            Step size for the pfail (x-axis). The default is 0.001.

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.x_data, self.y_data = get_oc(self.n_accept, self.sample_size, p_end, p_step)
        
    def update_curve(self, sample_size:int, acceptance_number:int, p_end:float=0.20, p_step:float=0.02)->None:
        """
        Update the sample plan parameters and then regenerate the oc curve data.

        Parameters
        ----------
        sample_size : int
            Sample size.
        acceptance_number : int
            Acceptance number.
        p_end : float, optional
            Ending step value for the pfail (x-axis). The default is 0.20.
        p_step : float, optional
            Step size for the pfail (x-axis). The default is 0.02.

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.sample_size = sample_size
        self.n_accept = acceptance_number
        self.make_data(p_end, p_step)
        
    def update_sample_size(self, sample_size:int)->None:
        """
        Update the sample size parameter and then regenerate oc curve data.

        Parameters
        ----------
        sample_size : int
            Sample size.

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.sample_size = sample_size
        self.make_data()
        
    def update_acceptance_number(self, n_accept:int)->None:
        """
        Update the acceptance number parameter and then regenerate oc curve data.

        Parameters
        ----------
        n_accept : int
            Acceptance number.

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.n_accept = n_accept
        self.make_data()