import numpy as np

from typings.sklearn.linear_model import LinearRegression


def example():
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 6, 8, 10])

    linreg = LinearRegression()
    linreg.fit(x, y)
