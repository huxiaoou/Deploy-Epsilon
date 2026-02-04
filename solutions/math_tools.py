import numpy as np
import pandas as pd


class COptimizer:
    def __init__(self, m: np.ndarray, v: np.ndarray):
        self.m = m
        self.v = v
        self.n = len(self.m)

    def optimize(self) -> np.ndarray:
        raise NotImplementedError


class COptimizerSign(COptimizer):
    def optimize(self) -> np.ndarray:
        sgn = np.sign(self.m)
        abs_sum = np.abs(sgn).sum()
        return sgn / abs_sum if abs_sum > 0 else self.m
