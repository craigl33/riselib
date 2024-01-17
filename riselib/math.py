import numpy as np


def normalize(values):
    min_value = np.min(values)
    max_value = np.max(values)
    normalized_values = (values - min_value) / (max_value - min_value)

    return normalized_values
