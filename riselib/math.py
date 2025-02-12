"""General math functions."""

import pandas as pd
import numpy as np
from scipy import stats

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




# def spline_interp_hrly_xr(y, res_min=30, dim='time'):
#     """
#     Spline interpolation of a time series to a higher resolution.
#     The function interpolates the time series to a higher resolution by using spline interpolation. The resolution is specified in minutes. The default resolution is 30 minutes. The function returns the interpolated time series.
#     """


#     res = '{}min'.format(res_min)

#     xnew = pd.date_range(start=y.time.values[0],
#                          end=pd.to_datetime(y.time.values[-1]) + datetime.timedelta(minutes=60-res_min),
#                          freq=res)

#     tck = xarray_extras.interpolate.splrep(y, dim)
#     ynew = xarray_extras.interpolate.splev(xnew, tck)

#     return ynew



def remove_outliers(df, column, n_std=3):
    """
    Remove outliers from a time series using standard deviation method
    """
    mean = df[column].mean()
    std = df[column].std()

    df = df.where(
        (df[column] <= mean + (n_std * std)) &
        (df[column] >= mean - (n_std * std))
    )

    return df

def remove_outliers_iqr(df, column):
    """
    Remove outliers using IQR method
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    df = df.where(
        ~((df[column] < (Q1 - 1.5 * IQR)) |
              (df[column] > (Q3 + 1.5 * IQR)))
    )

    return df

def detect_sudden_changes(df, column, window=5, threshold=3):
    """
    Detect and remove sudden changes/spikes
    """
    rolling_mean = df[column].rolling(window=window).mean()
    rolling_std = df[column].rolling(window=window).std()

    z_scores = np.abs((df[column] - rolling_mean) / rolling_std)
    df = df.where(z_scores < threshold)

    return df

def smooth_timeseries(df, column, window=5, new_column_name=False):
    """
    Smooth time series using moving average
    """
    if new_column_name:
        df[f'{column}_smoothed'] = df[column].rolling(window=window).mean()
    else:
        df[column] = df[column].rolling(window=window).mean()
        
    return df

def clean_timeseries(df, column, methods=['std', 'iqr', 'sudden_changes', 'positive'],
                     n_std=3, window=5, threshold=3, interpolation = 'linear'):
    """
    Clean time series data using multiple methods
    """

    df_copy = df.copy()

    if 'positive' in methods:
        df = df.where(df[column] > 0)

    if 'std' in methods:
        df = remove_outliers(df, column, n_std)

    if 'iqr' in methods:
        df = remove_outliers_iqr(df, column)

    if 'sudden_changes' in methods:
        df = detect_sudden_changes(df, column, window, threshold)

    if 'smooth' in methods:
        df = smooth_timeseries(df, column, window)
        

    ## Interpolate missing values, while also not dropping the first values (at window length)
    df.iloc[:window,:] = df_copy.iloc[:window,:]
    df = df.interpolate(interpolation)

    return df

