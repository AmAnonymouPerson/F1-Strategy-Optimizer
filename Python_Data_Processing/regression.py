import numpy as np
from scipy.optimize import minimize

def poly_model(x, coeffs):
    return sum(c * x**i for i, c in enumerate(reversed(coeffs)))


def run_regression(dataset, degree):

    x = dataset['TyreLife'].to_numpy()
    # x = x - x[0]
    y = dataset['LapTime'].to_numpy()

    initial_guess = np.full(degree + 1, 0.1)

    def loss(coeffs):
        y_pred = poly_model(x, coeffs)
        return np.sum((y - y_pred) ** 2)

    result = minimize(loss, initial_guess)
    best_coeffs = result.x

    x = np.array([])
    y = np.array([])

    return best_coeffs