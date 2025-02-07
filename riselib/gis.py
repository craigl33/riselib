"""General library for GIS operations."""

from shapely.geometry import Polygon
import glob
import pandas as pd
import numpy as np
import geopandas as gpd
import time
import rasterio
import h5py
from shapely.geometry import Point, Polygon
import progressbar
import rasterstats
from rasterio.merge import merge
from rasterio.plot import show
import os
from rasterstats import zonal_stats

import glob

from glob import glob
import os

def combine_shape_files(root_folder, id_text, crs = {'init': 'epsg:4326'}, subfolder=""):
    """Function to combine multi-part shape files from various countries in a single folder or location into a single
        GeoPandas dataframe"""
    
    search_path = os.path.join(root_folder, subfolder, f"*{id_text}*.shp")
    shp_files = glob(search_path, recursive=True)
    single_shp_file = gpd.GeoDataFrame(pd.concat([gpd.read_file(shp)for shp in shp_files]), crs= default_crs)

    return single_shp_file

def merge_raster(root_folder, subfolder, file_suffix, file_id, bounds, resolution):
    '''Function to search for and merge rasters from a common source, clip and resample at specified resolution'''
    
    search_path = os.path.join(root_folder, subfolder, f"*{file_id}*.{file_suffix}")
    files = glob(search_path, recursive=True)
    
    tiles = [rasterio.open(file) for file in files]
    
    merged_raster, merged_transform = rasterio.merge.merge(tiles, bounds = bounds, res=resolution)
    
    for tile in tiles:
        tile.close()
    
    ## single-band data so return this only
    
    return merged_raster, merged_transform
    
def write_raster(path, img, transform, crs={'init': 'epsg:4326'}, nodata=None):
    """Writes a raster array to a GeoTIFF file.

    Parameters
    ----------
    path : str
        Output file path
    img : numpy.ndarray
        Image data to write
    transform : affine.Affine
        Affine transform matrix
    crs : dict, optional
        Coordinate reference system, defaults to EPSG:4326
    nodata : float, optional
        Value to use for nodata pixels
    """
    """Writes a raster array to a GeoTIFF file."""
    width = img.shape[2] if len(img.shape) > 2 else img.shape[1]
    height = img.shape[1] if len(img.shape) > 2 else img.shape[0]

    out_kwargs = {'driver':'GTiff', 'dtype': img.dtype, 'nodata':nodata, 'width':width,
              'height':height, 'count':1, 'crs':crs, 'transform': transform,
              'tiled':False, 'interleave':'band'}

    with rasterio.open(path, "w", **out_kwargs) as dest:
        dest.write(img)
    
def create_geo_grid(adm_df, lat_res, lon_res, geom='poly', clip_lats=None):
    """Creates a regular geographic grid based on administrative boundaries.

    Parameters
    ----------
    adm_df : geopandas.GeoDataFrame
        Administrative boundaries
    lat_res : float
        Latitude resolution in degrees
    lon_res : float
        Longitude resolution in degrees
    geom : str, optional
        Geometry type ('poly' for polygons)
    clip_lats : tuple, optional
        Custom latitude/longitude bounds (lon1, lat1, lon2, lat2)

    Returns
    -------
    geopandas.GeoDataFrame
        Grid cells as geodataframe with administrative region information
    """
    """Creates a regular geographic grid based on administrative boundaries."""
    if clip_lats == None:
        lon1, lat1, lon2, lat2 = adm_df.total_bounds
    else:
        lon1, lat1, lon2, lat2 = clip_lats

    lon1 = np.floor(np.divide(lon1,lon_res))*lon_res
    lat1 = np.floor(np.divide(lat1,lat_res))*lon_res
    lon2 = np.ceil(np.divide(lon2,lon_res))*lon_res
    lat2 = np.ceil(np.divide(lat2,lat_res))*lat_res

    grid_lats = np.arange(lat1, lat2 +lat_res, lat_res)
    grid_lons = np.arange(lon1, lon2 +lon_res, lon_res)
    geom_poly = []
    geom_point = []
    lats = []
    lons = []

    with progressbar.ProgressBar(max_value=len(grid_lats)*len(grid_lons)) as bar:
        grid_count = 0
        for lon in grid_lons:
            for lat in grid_lats:
                poly = Polygon([(lon-lon_res/2, lat-lat_res/2), (lon+lon_res/2,lat-lat_res/2), (lon+lon_res/2,lat+lat_res/2),
                                (lon-lon_res/2,lat+lat_res/2), (lon-lon_res/2,lat-lat_res/2)])
                point = Point(lon, lat)
                geom_poly.append(poly)
                geom_point.append(point)
                lats.append(lat)
                lons.append(lon)
                grid_count += 1
                bar.update(grid_count)

    grid = gpd.GeoDataFrame({'grid_id':np.arange(0,len(geom_poly)), 'lat':lats, 'lon':lons},
                                    geometry=geom_poly, crs=adm_df.crs)
    grid = gpd.overlay(grid, adm_df, how='intersection', keep_geom_type=False)
    grid = grid.rename(columns={'index_right':'adm_id'})
    return grid

def create_ref_geo_grid(adm_df, lat_res, lon_res, bin_name='grid_bin', clip_lats=None):
    """Creates a reference geographic grid for binning and dimensional analysis.

    Parameters
    ----------
    adm_df : geopandas.GeoDataFrame
        Administrative boundaries
    lat_res : float
        Latitude resolution in degrees
    lon_res : float
        Longitude resolution in degrees
    bin_name : str, optional
        Name for the grid bin column
    clip_lats : tuple, optional
        Custom latitude/longitude bounds (lon1, lat1, lon2, lat2)

    Returns
    -------
    geopandas.GeoDataFrame
        Reference grid cells as geodataframe
    """
    """Creates a reference geographic grid for binning and dimensional analysis."""
    if clip_lats == None:
        lon1, lat1, lon2, lat2 = adm_df.total_bounds
    else:
        lon1, lat1, lon2, lat2 = clip_lats
    
    lon1 = np.floor(np.divide(lon1,lon_res))*lon_res
    lat1 = np.floor(np.divide(lat1,lat_res))*lon_res
    lon2 = np.ceil(np.divide(lon2,lon_res))*lon_res
    lat2 = np.ceil(np.divide(lat2,lat_res))*lat_res
    
    grid_lats = np.arange(lat1, lat2 +lat_res, lat_res)
    grid_lons = np.arange(lon1, lon2 +lon_res, lon_res)
    geom_poly = []
    geom_point = []
    lats = []
    lons = []
    
    with progressbar.ProgressBar(max_value=len(grid_lats)*len(grid_lons)) as bar:
        grid_count = 0
        for lon in grid_lons:
            for lat in grid_lats:
                poly = Polygon([(lon-lon_res/2, lat-lat_res/2), (lon+lon_res/2,lat-lat_res/2), (lon+lon_res/2,lat+lat_res/2),
                                (lon-lon_res/2,lat+lat_res/2), (lon-lon_res/2,lat-lat_res/2)])
                point = Point(lon, lat)
                geom_poly.append(poly)
                geom_point.append(point)
                lats.append(lat)
                lons.append(lon)
                grid_count += 1
                bar.update(grid_count)

    grid = gpd.GeoDataFrame({bin_name:np.arange(0,len(geom_poly)), 'lat':lats, 'lon':lons},
                                    geometry=geom_poly, crs=adm_df.crs)
    return grid

def simplify_geom_collection(geom):
    """Simplifies a geometry collection to a MultiPolygon.

    Parameters
    ----------
    geom : shapely.geometry
        Input geometry collection

    Returns
    -------
    shapely.geometry.MultiPolygon or original geometry
        Simplified geometry as MultiPolygon if input was a collection
    """
    """Simplifies a geometry collection to a MultiPolygon."""
    poly_list =[]
    if type(geom) == shapely.geometry.collection.GeometryCollection:
        for g in geom:
            if (type(g) == shapely.geometry.Polygon):
                poly_list.append(g)
        return shapely.geometry.MultiPolygon(poly_list)
    else:
        return geom