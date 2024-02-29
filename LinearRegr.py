import numpy as np

class LinearRegressionFromScratch:
    def __init__(self, fit_intercept=True):
        self.fit_intercept = fit_intercept
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]  # add a column of ones for the intercept term

        # Calculate coefficients using the normal equation
        self.coef_ = np.linalg.inv(X.T @ X) @ X.T @ y

        if self.fit_intercept:
            self.intercept_ = self.coef_[0]
            self.coef_ = self.coef_[1:]

    def predict(self, X):
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]
        return X @ np.concatenate([[self.intercept_], self.coef_])

