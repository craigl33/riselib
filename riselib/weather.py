"""Just a simple function to obtain the wind vector from the u and v components right now."""
import numpy as np


def obtain_wind_vector(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Obtain Wind Vector.

    This method calculates the wind speed and wind azimuth (direction) given the u (longitutde) and v (latitude)
     components of the wind vector.

    Args:
    ----
        u (np.ndarray): The u component of the wind vector.
        v (np.ndarray): The v component of the wind vector.

    Returns:
    -------
        tuple[np.ndarray, np.ndarray]: A tuple containing the wind speed and wind azimuth (direction) as numpy arrays.

    """
    # Wind speed
    wind_speed = np.sqrt(np.power(u, 2) + np.power(v, 2))

    # Wind azimuth (direction)
    # span the whole circle: 0 is north, π/2 is east, -π is south, 3π/2 is west
    azimuth = np.arctan2(u, v)
    wind_azimuth = np.where(azimuth >= 0, azimuth, azimuth + 2 * np.pi)

    return wind_speed, wind_azimuth
