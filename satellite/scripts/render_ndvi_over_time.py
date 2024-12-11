from __future__ import annotations

import concurrent.futures
import datetime
import io
import logging
import os
from venv import logger

import ee
import fire
import geemap
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from PIL import Image
from tqdm import tqdm

from satellite.utils import get_city_boundary
from satellite.utils import get_landsat_collection


def _initialize_ee() -> None:
    """Initialize Earth Engine."""
    project_name = os.getenv("EE_PROJECT_NAME")
    assert project_name, "Please set the EE_PROJECT_NAME environment variable"
    logger.info(f"Initializing Earth Engine with project {project_name}")
    ee.Initialize(project=project_name)


def _set_logging_level(log_level: str) -> None:
    """Set the logging level."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=numeric_level)


def _create_gif_from_tiff_dir(tiff_dir: str, output_gif: str, city_name: str) -> None:
    """Create a GIF from a directory containing TIFF files."""
    # Get a sorted list of TIFF files
    tiff_fpaths = sorted(
        [os.path.join(tiff_dir, fname) for fname in os.listdir(tiff_dir) if fname.endswith(".tif")],
    )

    # Create a list to store images for the GIF
    gif_frames = []

    # Define NDVI visualization range
    vmin, vmax = -1, 1

    # Loop through each TIFF and generate frames
    for tiff_fpath in tiff_fpaths:
        # Open the TIFF file
        with rasterio.open(tiff_fpath) as src:
            # Read the NDVI data
            ndvi = src.read(1)

            # Plot the NDVI using Matplotlib
            plt.figure(figsize=(8, 6))
            plt.imshow(ndvi, cmap="RdYlGn", vmin=vmin, vmax=vmax)
            plt.colorbar(label="NDVI")
            year = tiff_fpath.split("_")[-1].split(".")[0]
            plt.title(f"NDVI - {city_name} - {year}")
            plt.axis("off")

            # Save the plot to a buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            plt.close()
            buf.seek(0)

            # Load the PNG from buffer into Pillow and add to GIF frames
            gif_frames.append(Image.open(buf))

    # Save frames as a GIF
    gif_frames[0].save(
        output_gif,
        save_all=True,
        append_images=gif_frames[1:],
        duration=1000,  # Duration per frame in milliseconds
        loop=0,  # Infinite loop
    )
    logger.debug(f"GIF saved as {output_gif}")


def _generate_average_ndvi_plot(tiff_dir: str, plot_fpath: str, city_name: str) -> None:
    """Generate a plot of average NDVI over time."""
    tiff_fpaths = sorted(
        [os.path.join(tiff_dir, fname) for fname in os.listdir(tiff_dir) if fname.endswith(".tif")],
    )
    for tiff_fpath in tiff_fpaths:
        assert tiff_fpath.endswith(".tif"), f"Invalid TIFF file: {tiff_fpath}"
        # assert file endes with years
        assert tiff_fpath.split("_")[-1].split(".")[0].isdigit(), f"Invalid TIFF file: {tiff_fpath}"

    # List to store average NDVI values
    avg_ndvi_values = []

    # Loop through each TIFF and calculate the average NDVI
    for tiff_fpath in tiff_fpaths:
        # Open the TIFF file
        with rasterio.open(tiff_fpath) as src:
            # Read the NDVI data
            ndvi = src.read(1)
            # Calculate the average NDVI, ignoring NaN values
            avg_ndvi = np.nanmean(ndvi)
            avg_ndvi_values.append(avg_ndvi)

    # Extract years from the file names
    years = [int(tiff_fpath.split("_")[-1].split(".")[0]) for tiff_fpath in tiff_fpaths]

    # Plot the average NDVI over time
    plt.figure(figsize=(10, 6))
    plt.plot(years, avg_ndvi_values, marker="o", linestyle="-", color="b")
    plt.xlabel("Year")
    plt.ylabel("Average NDVI")
    plt.title(f"Average NDVI Over Time - {city_name}")
    plt.grid(True)
    plt.savefig(plot_fpath)
    plt.close()


def _process_year(year: int, roi, tiff_output_dir: str, scale: int = 100) -> None:
    """Process NDVI for a single year."""
    _initialize_ee()
    logger.debug(f"Processing year {year}")
    start_date = datetime.datetime(year, 1, 1)
    end_date = datetime.datetime(year, 12, 31)
    landsat_data = get_landsat_collection(roi, start_date, end_date)
    logger.debug(f"Landsat data: {landsat_data.getInfo()}")
    ndvi = landsat_data.normalizedDifference(["NIR", "RED"]).rename(f"NDVI_{year}")
    logger.debug(f"NDVI: {ndvi.getInfo()}")
    output_fpath = os.path.join(tiff_output_dir, f"ndvi_{year}.tif")
    logger.debug(f"Exporting NDVI image to {output_fpath}")
    geemap.ee_export_image(
        ndvi,
        filename=output_fpath,
        scale=scale,
        region=roi,
        file_per_band=False,
    )
    logger.debug(f"Exported NDVI image to {output_fpath}")


def main(
    city_name: str,
    start_year: int,
    end_year: int,
    output_dir: str,
    n_workers: int = 8,
    log_level: str = "INFO",
    scale: int = 100,
) -> None:
    """
    Render NDVI over time for the specified city.

    :param city_name: The name of the city for which to render NDVI over time.
    :param start_year: The start year for the NDVI time series.
    :param end_year: The end year for the NDVI time series.
    :param output_dir: The output directory for the rendered GIF and plots.
    :param n_workers: The number of workers to use for parallel processing.
    :param log_level: The logging level.
    :param scale: The scale for exporting NDVI images.
    """
    _set_logging_level(log_level)
    _initialize_ee()
    output_dir = os.path.join(output_dir, city_name)
    tiff_output_dir = os.path.join(output_dir, "tiff")
    os.makedirs(tiff_output_dir, exist_ok=True)
    roi = get_city_boundary(city_name).geometry()

    # Process NDVI for each year in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [
            executor.submit(_process_year, year, roi, tiff_output_dir, scale)
            for year in range(start_year, end_year + 1)
        ]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            future.result()

    # Create GIF from TIFF files
    output_gif = os.path.join(output_dir, "ndvi_over_time.gif")
    _create_gif_from_tiff_dir(tiff_output_dir, output_gif, city_name)

    # Generate average NDVI plot
    plot_fpath = os.path.join(output_dir, "average_ndvi.png")
    _generate_average_ndvi_plot(tiff_output_dir, plot_fpath, city_name)


if __name__ == "__main__":
    fire.Fire(main)
