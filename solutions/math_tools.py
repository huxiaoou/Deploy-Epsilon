import numpy as np
import pandas as pd
from typing import Union
from sklearn.covariance import LedoitWolf, GraphicalLassoCV

"""
-----------------------------
--- Covariance Estimation ---
-----------------------------
"""


class _CCovEst:
    def __init__(self, X: Union[np.ndarray, pd.DataFrame]):
        """_summary_

        Args:
            X (np.ndarray): a sample matrix, shape = (n_samples, k_features)
        """
        self.X = X.to_numpy() if isinstance(X, pd.DataFrame) else X
        self.n, self.k = X.shape

    def cov(self) -> np.ndarray:
        raise NotImplementedError


class CCovEstSample(_CCovEst):
    def cov(self) -> np.ndarray:
        return np.cov(self.X, rowvar=False)


class CCovEstLW(_CCovEst):
    """_summary_
    Ledoit Wolf method for sample covariance estimation
    """

    def cov(self) -> np.ndarray:
        c = LedoitWolf().fit(self.X)
        return c.covariance_


class CCovEstGL(_CCovEst):
    """_summary_
    Graphical Lasso method for sample covariance estimaiton
    """

    def cov(self) -> np.ndarray:
        c = GraphicalLassoCV(alphas=5, n_refinements=3, cv=5).fit(self.X)
        return c.covariance_


"""
-----------------
--- Optimizer ---
-----------------
"""


class COptimizer:
    def __init__(self, m: np.ndarray, v: np.ndarray):
        """_summary_

        Args:
            m (np.ndarray): estimation of returns on n assets, should be n by 1 vector(array).
            v (np.ndarray): estimation of covariance on n assets, should be n by n matrix
        """
        self.m = m
        self.v = v
        self.n = len(self.m)

    def optimize(self) -> np.ndarray:
        raise NotImplementedError


class COptimizerEq(COptimizer):
    def optimize(self) -> np.ndarray:
        return np.ones(self.n) / self.n


class COptimizerSign(COptimizer):
    def optimize(self) -> np.ndarray:
        sgn = np.sign(self.m)
        abs_sum = np.abs(sgn).sum()
        return sgn / abs_sum if abs_sum > 0 else self.m


class COptimizerLbd(COptimizer):
    def __init__(self, m: np.ndarray, v: np.ndarray, lbd: float):
        super().__init__(m, v)
        self.lbd = lbd

    def optimize(self) -> np.ndarray:
        si = np.linalg.inv(self.v)
        one = np.ones(self.n)
        a = one @ si @ one
        b = one @ si @ self.m
        delta = (self.lbd - b) / a
        w = si @ (self.m + delta * one) / self.lbd
        return w
