"""Collect and filter relevant Copernicus ERA5 data.

The data is loaded from a network drive and returned as an xarray. All variables within that directory are available
 for loading and filtering by time, longitude, and latitude. The main functions within the module is `get_era_data`.

Example usage:
    # Get data for a all wind variables, filtered by time, longitude, and latitude
    era_data = get_era_data(
        variables=['wind'],
        time=slice('2010-01', '2010-02'),
        longitude=slice(40, 50),
        latitude=slice(40, 50),
        whole_number_offset=True,
    )


This library seems to be outdated and may be able to be deleted.
"""




import glob
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
import xarray as xr

from riselib.utils.logger import Logger

log = Logger(__name__)

GLOBAL_ERA5_DIR = Path(r'//vfiler2/statsdata/WeatherData/Data_from_Copernicus')

# def get_era5_data():

VAR_TO_FILE_ALIAS_DICT = dict(
    wind='Wind_10',
    wind_10='Wind_10_',
    wind10='Wind_10_',
    wind_100='Wind_100_',
    wind100='Wind_100_',
    u10='Wind_10_u',
    v10='Wind_10_v',
    u100='Wind_100_u',
    v100='Wind_100_v',
)


def _get_years_from_time_sel(time_sel: str | slice | None) -> list:
    """Get a list of years from a time selection. Multiple formats are supported.

    Args:
    ----
        time_sel: A string, a slice, or None.
            - If `time_sel` is a string, it represents a specific date or time in string format.
              The method will convert it to a datetime object and return a list containing the year of that datetime
              object.
            - If `time_sel` is a slice, it represents a range of dates or times.
              The method will convert the start and stop values of the slice to datetime objects, and return a list of
              years between those two dates inclusive.
            - If `time_sel` is None, the method will return a list of unique years from the year 1972 to the current
            year.
            - If `time_sel` is of any other type, a TypeError will be raised.

    Returns:
    -------
        A list of years, represented as integers, corresponding to the time selection provided by `time_sel`.

    Raises:
    ------
        TypeError: If the `time_sel` parameter is not of type str, slice, or None.

    """
    if isinstance(time_sel, str):
        return [pd.to_datetime(time_sel).year]
    elif isinstance(time_sel, slice):
        return list(range(pd.to_datetime(time_sel.start).year, pd.to_datetime(time_sel.stop).year + 1))
    elif time_sel is None:
        return pd.date_range('1972-01-01', 'now').year.unique().tolist()
    else:
        msg = f'Unknown time_sel type {type(time_sel)}.'
        raise TypeError(msg)


def get_era_data(
    variables: list | str,
    longitude: slice | list,
    latitude: slice | list,
    time: str | slice | None,
    whole_number_offset: bool = False,
) -> xr.Dataset:
    """Get ERA5 data for given variables, longitude, latitude and time.

    Data is loaded from specified directory on a network drive. This allows for faster loading and no need create a
    extra copy of the data somewhere. To see a full list of available variables, check the directory under:
    //vfiler2/statsdata/WeatherData/Data_from_Copernicus
    To load all variables from _Wind_100_v_data_Copernicus_hourly_* files, use 'wind_100' to get both u and v, and use
    'wind_100_v' to get only v. There are also some aliases defined in VAR_TO_FILE_ALIAS_DICT.

    Args:
    ----
        variables (list|str): List of variables to load. Can also be a single variable as string.
        longitude (slice|list): Longitude range to load. Can also be a list of specific longitudes.
        latitude (slice|list): Latitude range to load. Can also be a list of specific latitudes.
        time (str|slice|None): Time range to load. Can also be a single time as string, (e.g. '2010-01') or a slice
            (e.g. slice('2010-01', '2010-02')). If None, all available data is loaded.
        whole_number_offset (bool): If True, longitude and latitude are offset by 0.125 to match the grid cell
            borders (e.g. 40.125->40.0, 40.0->39.875).

    """
    if isinstance(variables, str):
        variables = [variables]

    # Get list of years from time selection to not load unnecessary data
    years = _get_years_from_time_sel(time)

    # Generate relevant file names
    file_names = []
    for var in variables:
        if var in VAR_TO_FILE_ALIAS_DICT:
            file_names.append(VAR_TO_FILE_ALIAS_DICT[var])
        else:
            file_names.append(var)
    file_names = list(set(file_names))  # Drop duplicates

    # Generate list of file paths
    file_paths = []
    for year in years:
        for file_name in file_names:
            file_paths.extend(glob.glob(str(GLOBAL_ERA5_DIR / str(year) / f'_{file_name}*.nc')))

    if not file_paths:
        msg = f'No files found for variables {variables} (file_names: {file_names}) and time {time} (years: {years}).'
        raise FileNotFoundError(msg)

    # Load data
    era_data = xr.open_mfdataset(file_paths, chunks={'time': 96})

    # Check if latitude data is in descending order and sort if not
    if isinstance(latitude, slice) and latitude.start < latitude.stop:
        latitude = slice(latitude.stop, latitude.start, latitude.step)
        log.info('Latitude data was not in descending order. Sorted it now.')
    if isinstance(latitude, Sequence) and latitude != sorted(latitude, reverse=True):
        latitude = sorted(latitude, reverse=True)
        log.info('Latitude data was not in descending order. Sorted it now.')

    # Apply selection
    era_data = era_data.sel(time=time, longitude=longitude, latitude=latitude)

    # Offset lat/lon to whole numbers
    if whole_number_offset:
        era_data = era_data.assign_coords(
            longitude=era_data.longitude + 0.125,  # Moves east (range is -180 to 180)
            latitude=era_data.latitude - 0.125,  # Moves north (range is 90 to -90)
        )

    return era_data


# This is just for testing and can be ignored/ removed
if __name__ == '__main__':
    import geopandas as gpd

    grid_data = gpd.read_feather('U:/GIS/Ukraine/3-dev/20230613_ukr_selection_summary_rev4_COMPLETE.feather')
    # Drop potential duplicates
    grid_data = grid_data.drop_duplicates(subset=['lat', 'lon'])

    era_data = get_era_data(
        variables=['wind'],
        time=slice('2010-01', '2010-02'),
        longitude=slice(-100000, 100000),
        latitude=slice(100, 85),
        whole_number_offset=True,
    )
