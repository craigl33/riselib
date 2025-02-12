"""

General library for GIS operations.

GIS-SCRIPT contains some of these functions, but these should probably be seperated out from it and put in a more generally available package (such as this)

"""

from shapely.geometry import Polygon
import pandas as pd
import numpy as np
import geopandas as gpd

import rasterio

from rasterio.merge import merge
from rasterio.plot import show
import os
from pyproj import CRS
import cartopy.io.shapereader as shpreader
from pathlib import Path

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

#### These are duplicated functions from gis-script
# In the long-term, the general gis-script functions should be moved to a new library 
# similar to riselib/gis.py that allows this functionality to be shared without having to
# install a long list of requirements for the gis-script package
# 
def get_country_gdf(country_identifier: str, 
                    db_name = 'admin_0_countries',
                    return_data: bool = False,
                    crs: CRS = CRS('EPSG:4326')
                      ) -> gpd.GeoDataFrame:
    """Get the GeoDataFrame of a country based on its identifier (name, ISO2 or ISO3 code).

    Args:
    ----
        country_identifier: Identifier of the country. Can be the name, ISO2 or ISO3 code.
        db_name: Name of the Natural Earth database. By default, uses the standard admin0, but
                this can vary for the inclusion of occupied territories, etc. Refer
                to Natural Earth github for more info (https://github.com/nvkelso/natural-earth-vector/)
        additional_identifier: The use of POV databases (see db_name above) doesnt seem to work. 
                As an alternative, this builds in the functionality of having multiple additional
                country identifiers to add to the GDF. This is a quick fix. 
        return_data: Whether to return the data of the country. Defaults to False.
        crs: Coordinate reference system of the GeoDataFrame. Defaults to EPSG:4326.

    Returns:
    -------
        gpd.GeoDataFrame: GeoDataFrame of the country.

    """
    shp_filename = shpreader.natural_earth(resolution='10m', category='cultural', name= db_name)
    shp = shpreader.Reader(shp_filename)

    # Check if the attributes are upper or lowercased
    if "admin_0" in db_name:
        country_record = list(
        filter(
            lambda c: c.attributes['NAME_EN'] == country_identifier
            or c.attributes['ISO_A2'] == country_identifier
            or c.attributes['ISO_A3'] == country_identifier,
            shp.records(),
        )
    )

    ### This isnt working        
    elif "admin_1" in db_name:
        country_record = list(
        filter(
            lambda c: c.attributes['admin'] == country_identifier
            or c.attributes['iso_a2'] == country_identifier
            or c.attributes['adm0_a3'] == country_identifier,
            shp.records(),
        )
    ) 
            # This is really just to rename the admo_a3 to ISO_A3 for consistency. not that necessary
        rename_cols = {'adm0_a3':'ISO_A3'}
    else:
        raise ValueError('Country identifier not found in shapefile or attempt was made to get granularity finer than admin_1.')

    if len(country_record) == 0:
        msg = f'Country identifier {country_identifier} not found.'
        raise ValueError(msg)
    elif (len(country_record) > 1)&('admin_0' in db_name):
        msg = f'Country identifier {country_identifier} is ambiguous for an ADM0 identifier. Found {len(country_record)} matches.'
        raise ValueError(msg)
    else:
        country_record = country_record

    # Create gdf from country_record.geometry multi-polygon.
    # For return data, the filtering is actually not working
    if return_data:
        
        gdf = gpd.GeoDataFrame(data=[c.attributes for c in country_record], geometry=[c.geometry for c in country_record])
        gdf = gdf.rename(columns=rename_cols)
        gdf.columns = gdf.columns.str.upper()
        gdf = gdf.rename(columns={'GEOMETRY':'geometry',})
        gdf = gdf.set_crs(crs)
    else:
        gdf = gpd.GeoDataFrame(geometry=[c.geometry for c in country_record])
        gdf = gdf.set_crs(crs)

    return gdf


def get_country_bounds(country_identifier: str, shp_file_additions: str | Path | gpd.GeoDataFrame = None, db_name: str = 'admin_0_countries', rounding: np.float64 = None) -> tuple:
    """Get the bounding box of a country based on its identifier (name, ISO2 or ISO3 code).

    Next to the identifier a shapefile can also be passed. The shapefile will then extend the bounding box of the
    selected country to include the shapefile. Can be used for EEZ areas for example.

    Args:
    ----
        country_identifier (str): Identifier of the country. Can be the name, ISO2 or ISO3 code.
        shp_file_additions (str | Path | gpd.GeoDataFrame, optional): Shapefile to extend the bounding box. Defaults
            to None.
        db_name: By default, uses the standard admin0, but this can vary for the inclusion of occupied territories, etc. 
            Refer to Natural Earth github for more info (https://github.com/nvkelso/natural-earth-vector/)
        rounding: Rounding of the bounding box. Defaults to None.

    Returns:
    -------
        tuple: Bounding box of the country in the form (x1, y1, x2, y2) rounded to the nearest 0.25 (as default).

    """
    gdf = get_country_gdf(country_identifier, db_name=db_name)

    if shp_file_additions is not None:
        if isinstance(shp_file_additions, (str, Path)):
            gdf_addition = gpd.read_file(shp_file_additions)
            gdf_addition = gdf_addition.to_crs(gdf.crs)
        elif isinstance(shp_file_additions, gpd.GeoDataFrame):
            gdf_addition = shp_file_additions
            gdf_addition = gdf_addition.to_crs(gdf.crs)

        gdf = pd.concat([gdf, gdf_addition], ignore_index=True)
    
    x1, y1, x2, y2 = gdf.geometry.total_bounds
    if rounding is not None:
        x1 = np.floor(x1 / rounding) * rounding
        x2 = np.ceil(x2 / rounding) * rounding
        y1 = np.floor(y1 / rounding) * rounding
        y2 = np.ceil(y2 / rounding) * rounding        

    return x1, y1, x2, y2    

