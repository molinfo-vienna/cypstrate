from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.utils.validation import check_is_fitted
import numpy as np

__all__ = ["ConsensusClassifier"]


class ConsensusClassifier(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        estimators,
        input_sizes,
        voting="majority",
        prob_threshold=0.5,
        min_consensus=3,
    ):
        self.input_sizes = input_sizes  # the input size accepted by every estimator -> important to split up the X-array
        # in the scikit API
        self.estimators = estimators
        self.min_consensus = min_consensus
        self.voting = voting
        self.prob_threshold = prob_threshold

    def _validate_X_predict(self, X):
        n_features = X.shape[1]
        if self.n_features_ != n_features:
            raise ValueError(
                "Number of features of the model must "
                "match the input. Model n_features is %s and "
                "input n_features is %s " % (self.n_features_, n_features)
            )
        return X

    def _split_X_for_estimators(self, X):
        # splits up the X-array according to the length of the feature arrays used
        sections = np.cumsum(self.input_sizes)[:-1]

        X_splits = np.split(X, sections, axis=1)
        return X_splits

    def fit(self, X, y):
        if not self.voting in ["max", "hard", "soft"]:
            raise ValueError(
                "Mode {} is not valid for combination of consensus_results.".format(
                    self.voting
                )
            )

        # VERY IMPORTANT FOR X: the different feature sets have to be calculated according to the different feature sets
        # used and then passed to the fit function. This is done in this rather ugly way due to compatibility with the
        # scikit learn API
        if len(self.estimators) < 2:
            raise ValueError(
                "There must be at least 2 estimators for the consensus approach to be of any use"
            )

        # Somehow needed for a classifier to work in the whole sklearn api:w
        self.classes_, y = np.unique(y, return_inverse=True)

        self.n_features_ = sum(self.input_sizes)
        X = self._validate_X_predict(X)

        self.estimators_ = []
        for estimator, X_slice in zip(self.estimators, self._split_X_for_estimators(X)):
            self.estimators_.append(clone(estimator).fit(X_slice, y))

        return self

    def _collect_probas(self, X):
        consensus_preds = [
            estimator.predict_proba(X_slice)
            for estimator, X_slice in zip(
                self.estimators_, self._split_X_for_estimators(X)
            )
        ]
        pos_proba_vectors = np.asarray(consensus_preds)

        return pos_proba_vectors

    def _hard_voting(self, X):
        preds = np.argmax(self._collect_probas(X), axis=2)
        bin_counts = np.apply_along_axis(np.bincount, minlength=2, axis=0, arr=preds)

        consensus_preds = []
        for bin_count in bin_counts.T:
            if np.max(bin_count) >= self.min_consensus:
                consensus_preds.append(np.argmax(bin_count))
            else:
                consensus_preds.append(np.nan)

        return consensus_preds

    def predict_proba(self, X):
        check_is_fitted(self)

        if self.voting == "soft":
            return np.mean(self._collect_probas(X), axis=0)
        elif self.voting == "max":
            return np.max(self._collect_probas(X), axis=0)
        else:
            raise ValueError(
                "Allowed voting strategies for predict_proba are 'max' and 'soft'."
            )

    def predict(self, X):
        check_is_fitted(self)

        if self.voting == "max" or self.voting == "soft":
            return np.argmax(self.predict_proba(X), axis=1)
        elif self.voting == "hard":
            return self._hard_voting(X)
