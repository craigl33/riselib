"""General math functions."""
import numpy as np


def normalize(values: np.ndarray) -> np.ndarray:
    """Normalize the values in a given array.

    It is a min-max normalization, which scales the values to a range of 0 to 1.

    Args:
    ----
        values: An array containing the values to be normalized.

    Returns:
    -------
        An array containing the normalized values.

    Example:
    -------
        >>> values = [1, 2, 3, 4, 5]
        >>> normalize(values)
        [0.0, 0.25, 0.5, 0.75, 1.0]

    """
    min_value = np.min(values)
    max_value = np.max(values)
    normalized_values = (values - min_value) / (max_value - min_value)

    return normalized_values
