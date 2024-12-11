"""Utility functions for the satellite image analysis project."""
from __future__ import annotations

import logging
from datetime import datetime

import ee
import geemap
import osmnx

logger = logging.getLogger(__name__)


def get_landsat_collection(roi: ee.Geometry, start_date: datetime, end_date: datetime) -> ee.Image:
    """
    Retrieves the median Landsat image for a given region of interest and date range.

    Depending on the date range, the function selects the appropriate Landsat satellite:
    - Landsat 8 for years 2013 onwards
    - Landsat 7 for years 1999 to 2012
    - Landsat 5 for years before 1999

    The function filters the image collection by the specified date range and selects the
    Near-Infrared (NIR) and Red (RED) bands.
    :param roi: The region of interest.
    :param start_date: The start date for the date range.
    :param end_date: The end date for the date range.
    :return: The median Landsat image for the specified date range.
    """
    assert start_date < end_date, "Start date must be before end date."

    start_year = start_date.year
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    if start_year >= 2013:
        # Use Landsat 8 for years 2013 onwards
        dataset_name = "LANDSAT/LC08/C02/T1_L2"
        bands = ["SR_B5", "SR_B4"]
    elif start_year >= 1999:
        # Use Landsat 7 for years 1999 to 2012
        dataset_name = "LANDSAT/LE07/C02/T1_L2"
        bands = ["SR_B4", "SR_B3"]
    else:
        # Use Landsat 5 for years before 1999
        dataset_name = "LANDSAT/LT05/C02/T1_L2"
        bands = ["SR_B4", "SR_B3"]

    logger.debug(f"Retrieving Landsat data {dataset_name} ({bands}) for {start_date_str} to {end_date_str}")

    return (
        ee.ImageCollection(dataset_name)
        .filterBounds(roi)
        .filterDate(start_date_str, end_date_str)
        .select(bands)
        .map(lambda image: image.rename(["NIR", "RED"]))
        .median()
    )


def get_place_boundary(place_name: str) -> ee.Geometry:
    """
    Retrieves the boundary geometry for a given place name.

    :param place_name: The name of the place for which to retrieve the boundary.
    :returns: The geometry of the place's boundary if found, otherwise None.
    """
    logger.debug(f"Retrieving boundary for place {place_name}")
    place_geometry_gdf = osmnx.geocode_to_gdf(place_name)
    return geemap.geopandas_to_ee(place_geometry_gdf)
