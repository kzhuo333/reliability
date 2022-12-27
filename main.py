from scipy.stats import binom
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple


def binom_p(k:int, n:int, p_end:float=1.0, p_step:float=0.0005):
    x = list(np.arange(0.0, p_end, p_step))
    y = [binom.pmf(k,n,p) for p in x]
    return x, y

def binom_k(n:int, p:float):
    x = list(range(0, n, 1))
    y = [binom.pmf(k,n,p) for k in x]
    return x, y

def get_area(x:List[float], y:List[float]):
    """
    

    Parameters
    ----------
    x : List[float]
        DESCRIPTION.
    y : List[float]
        DESCRIPTION.

    Returns
    -------
    area : TYPE
        x and y must contain the same number of elements
        x and y must have at least 2 elements
        

    """
    
    area = 0.0
    for i in range(0, len(x)-1):
        xn = x[i]
        xnn = x[i+1]
        yn = y[i]
        ynn = y[i+1]
        
        area = area + 0.5 * (xnn-xn) * (ynn+yn)
        
    return area

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
    

def get_nearest_index(x:List[float], target:float)->int:
    """
    Find index of element in list which is closest to target

    Parameters
    ----------
    x : List[float]
        List to find index of element closest to target.
    target : float
        Target value.

    Returns
    -------
    int
        The index of element closest to target.

    """
    
    d = {idx:abs(target-xx) for idx, xx in enumerate(x)}
    return min(d, key=d.get)

def get_envelope(x:List[float], target:float)->Tuple[int, int]:
    
    d = [(idx, abs(target-xx)) for idx, xx in enumerate(x)]
    d.sort(key = lambda xx: xx[1])
    return d[0][0], d[1][0]

def get_ql(k:float, n:float, pval:float)->float:
    """
    Get the quality limit on the OC curve (defined by k and n) corresponding to the given pval.

    Parameters
    ----------
    k : float
        Acceptance number for sample plan.
    n : float
        Sample size for sample plan.
    pval : float
        Probability of acceptance (y-axis on the OC curve).

    Returns
    -------
    float
        The quality limit (x-axis of the OC curve) corresponding to the pval.

    """
    
    x, y = get_oc(k, n)
    idx = get_nearest_index(y, pval)
    return x[idx]

class sample_plan:
    def __init__(self, ss:int, n_accept:int):
        self.sample_size = ss
        self.n_accept = n_accept

class oc_curve:
    def __init__(self, sample_size:int = 300, acceptance_number:int= 3, alpha:float = 0.05, beta:float = 0.10)->None:
        self.sample_size = sample_size
        self.n_accept = acceptance_number
        self.alpha = alpha
        self.beta = beta
        self.make_data()
    
    def make_data(self, p_end:float=0.20, p_step:float=0.001):
        self.x_data, self.y_data = get_oc(self.n_accept, self.sample_size, p_end, p_step)
        
    def update_curve(self, sample_size:int, acceptance_number:int, p_end:float=0.20, p_step:float=0.02):
        self.sample_size = sample_size
        self.n_accept = acceptance_number
        self.make_data(p_end, p_step)
        
    def update_sample_size(self, sample_size:int):
        self.sample_size = sample_size
        self.make_data()
        
    def update_acceptance_number(self, n_accept:int):
        self.n_accept = n_accept
        self.make_data()

plan = sample_plan(300, 3)

x,y = get_oc(plan.n_accept, plan.sample_size, 0.20, 0.001)
#plt.scatter(x, y)
plt.plot(x,y, linestyle='dashed', marker='x')
plt.title(f"OC Curve (n={plan.sample_size}, k={plan.n_accept})")
plt.ylabel("Probability of Acceptance")
plt.xlabel("Lot Probability Defective")
plt.grid()
plt.ylim(ymax = 1.0, ymin = 0.0)
plt.xlim(xmax = 0.1, xmin = 0.0)
