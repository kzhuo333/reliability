"""Module for standard Weibull statistics.
"""
import math

def pdf(t:float, m:float, c:float)-> float:
    """Weibull probability distribution function.

    Args:
        t (float): variable
        m (float): shape parameter
        c (float): scale parameter aka characteristic life

    Returns:
        float: result
    """
    p = - pow(t/c, m)
    m/t * pow(t/c, m) * pow(math.e, p)

def cdf(t:float, m:float, c:float)-> float:
    """Weibull cumulative distribution function.

    Args:
        t (float): variable
        m (float): shape parameter
        c (float): scale parameter aka characteristic life

    Returns:
        float: result
    """
    p = - pow(t/c, m)
    return 1.0-pow(math.e, p)

def hazard(t:float, m:float, c:float)-> float:
    """Weibull hazard function aka failure rate.

    Args:
        t (float): variable
        m (float): shape parameter
        c (float): scale parameter aka characteristic life

    Returns:
        float: result
    """
    return m/t * pow(t/c, m)