from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.preprocessing import StandardScaler
import numpy as np


__all__ = ["NonBinaryScaler"]


class NonBinaryScaler(TransformerMixin, BaseEstimator):
    def __init__(self, with_mean=True, with_std=True):
        self.with_mean = with_mean
        self.with_std = with_std
        self.scaler = StandardScaler(with_mean=with_mean, with_std=with_std, copy=False)

    def get_nonbinary_mask(self, X):
        sorted_array = np.sort(X, axis=0)
        unique_counts = (sorted_array[1:, :] != sorted_array[:-1, :]).sum(axis=0) + 1
        non_binary = unique_counts != 2

        return non_binary

    def fit(self, X, y=None):
        self.nonbinary_mask = self.get_nonbinary_mask(X)
        self.scaler.fit(X[:, self.nonbinary_mask], y)
        return self

    def transform(self, X):
        X_new = X.copy()
        X_new[:, self.nonbinary_mask] = self.scaler.transform(
            X_new[:, self.nonbinary_mask], copy=False
        )
        return X_new
