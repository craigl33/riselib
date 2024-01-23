import glob
from pathlib import Path

import pandas as pd
import xarray as xr

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


def get_years_from_time_sel(time_sel):
    if isinstance(time_sel, str):
        return [pd.to_datetime(time_sel).year]
    elif isinstance(time_sel, slice):
        return list(range(pd.to_datetime(time_sel.start).year, pd.to_datetime(time_sel.stop).year + 1))
    elif time_sel is None:
        return pd.date_range('1972-01-01', 'now').year.unique().tolist()
    else:
        raise TypeError(f'Unknown time_sel type {type(time_sel)}.')


def get_era_data(variables, longitude, latitude, time=None, selection_method='nearest'):
    # Get list of years from time selection to not load unnecessary data
    years = get_years_from_time_sel(time)

    # Generate relevant file names
    file_names = []
    for var in variables:
        if var in VAR_TO_FILE_ALIAS_DICT.keys():
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
        raise FileNotFoundError(
            f'No files found for variables {variables} (file_names: {file_names}) and time {time} (years: {years}).'
        )

    # Load data
    era_data = xr.open_mfdataset(file_paths, chunks={'time': 96})

    # Apply selection
    era_data = era_data.sel(time=time)  # , longitude=longitude, latitude=latitude)

    return era_data


if __name__ == '__main__':
    # This is just for testing and can be ignored/ removed
    import geopandas as gpd

    grid_data = gpd.read_feather('U:/GIS/Ukraine/3-dev/20230613_ukr_selection_summary_rev4_COMPLETE.feather')
    # Drop potential duplicates
    grid_data = grid_data.drop_duplicates(subset=['lat', 'lon'])

    era_data = get_era_data(
        variables=['wind'], time=slice('2010-01', '2010-02'), longitude=slice(40, 50), latitude=slice(40, 50)
    )
    era_data
