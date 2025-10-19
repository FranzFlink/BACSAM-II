# BACSAM-II

This repository summarizes the codespace for **processing**, **analyzing**, and **visualizing** data from the **BACSAM-II campaign**.

---

## Data Structure

The **BACSAM-II** data is organized into three main categories:

- **Model output** (e.g., ICON)
- **Observations** (e.g., Polar 6 meteorological data, buoys, satellite data)
- **Reanalysis data** (e.g., ERA5, CARRA)

```
/data
    /model_output
        /raw
        /processed
        /ar
    /observations
        /raw
            /polar6
                /noseboom
                    /1hz
                        Flight_YYYYMMDD_P6_XX_1Hz.asc
                    /100hz
                        Flight_YYYYMMDD_P6_XX_100Hz.asc
                /radiation_kt19
                        BACSAM2_BBR_RFXX.dat
                /aerosol
                /fisheye
            /t-bird
                /noseboom
                    /1hz
                        Flight_YYYYMMDD_TB_XX_1Hz_tb.asc
                    /100hz
                        Flight_YYYYMMDD_TB_XX_100Hz_tb.asc
                /aerosol
            /buoys
            /satellite
                /modis
                    /mod29
                        MOD29E1D_AYYYYJJ_*_*_MOD_Grid_Seaice_4km_North_Ice_Surface_Temperature_NP_*.tif # J is the Julian day
                    /mod021
                        MOD021KM.AYYYYJJ.HHMM.*.*.hdf

                /sentinel-2
        /processed
            /polar6_unified
                noseboom_unified.nc
                radiation_kt19_unified.nc
                aerosol_unified.nc
                fisheye_unified.mp4 # a low-res video file of all fisheye images combined
            /t-bird_unified
                noseboom_unified.nc
                aerosol_unified.nc
            /buoys_unified
            /satellite_unified
                modis_unified.nc    # optimally already on the same grid as sentinel-2
                sentinel2_unified.nc
        /ar
    /reanalysis
        /raw
        /processed
        /ar
```

### Folder Descriptions

- `/data/*/raw`: Contains raw data files. These can be large (1 - 100 GB) and come in various formats (e.g., GRIB, HDF5, CSV). Multiple files per variable and time period are expected.  
- `/data/*/processed`: Contains unified, cleaned, and processed data. These files are smaller (<1 GB) and easy to share, typically stored in **NetCDF** format following **CF conventions** where possible.  
- `/data/*/ar`: Contains **analysis-ready (AR)** data files, often aggregated or subsetted for specific analyses or visualizations. Also stored in **NetCDF** format.

---

## Code Organization

The code is divided into distinct directories for clarity and reproducibility.

```
/book
    /notebooks
        /processing        # Demonstration & exploration notebooks; each should have a matching script in /scripts
        /data_analysis     # Main data analysis notebooks; should also have matching scripts in /scripts
        /visualizations    # Visualization notebooks; matching scripts are optional

/scripts
    /processing            # Scripts for converting raw data → processed data
    /data_analysis         # Scripts for creating analysis-ready (AR) data from processed data

/lib
    custom_style_lib.py    # Custom plotting styles and themes; ensures consistent visualization aesthetics
    helper.py              # Helper functions for data processing, analysis, and visualization
```

---

## Notes

- All shared data should ideally be **<1 GB** per dataset.  
- Plots should use styles from `custom_style_lib.py` to maintain a consistent look.  
- Any exploratory notebooks should link to corresponding scripts to ensure reproducibility. We should try to track changes primarily through scripts rather than notebooks. 
- Each notebook should clearly state its purpose (exploration, analysis, visualization) at the top; In general the vision would be to have a full jupyter book as documentation for the project. For now, this README serves as a high-level overview.
- xarray and pandas should be the primary libraries for data handling. Matplotlib and seaborn for plotting, with hvplot for interactive visualizations.
- TODO:
    - Define naming conventions for files in each data folder.
    - Create templates for notebooks and scripts to ensure consistency.
        - NAMING CONVENTIONS FOR SCRIPTS AND NOTEBOOKS!!! 
---

## Repository contents (concise)

Below is a short, file/folder-level listing of what's in this repository with a one-line description for each entry. It matches the workspace snapshot and keeps the descriptions minimal and factual.

- `book/` — Jupyter Book sources; contains notebooks used for documentation and analysis.
    - `book/notebooks/data_analysis/buoy_modis.ipynb` — Notebook that compares buoy observations with MODIS satellite data (regridding and bias maps).
    - `book/notebooks/processing/` — Example processing notebooks (demonstrations and helpers).

- `data/` — All datasets (raw, processed, reanalysis). Organized into `model_output`, `observations`, `reanalysis` with `raw`/`processed`/`ar` subfolders.

- `legacy/` — Older scripts, notebooks, raw notes and example runs from prior work (useful references; not necessarily production-ready).

- `lib/` — Small python libraries used across notebooks and scripts (e.g., `custom_style_lib.py` for plotting styles).

- `scripts/` — Main runnable scripts organized by purpose:
    - `scripts/processing/` — Data processing scripts (convert raw → processed, preprocessing). Example: `sentinel-2_download_and_process.py` (Earth Engine-based download + processing).
    - `scripts/` — Small utilities and analysis scripts (e.g., `profile.py`, `sim_solar.py`).

- `README.md` — This file: high-level overview and notes about structure, dependencies and TODOs.

Notes:
- Every top-level folder above contains multiple files and subfolders; consult those folders for per-file details. The `book/notebooks/data_analysis/buoy_modis.ipynb` notebook uses `xarray`, `xesmf`, and `pandas` and demonstrates regridding buoy observations to MODIS grid and computing bias maps.
- For runnable scripts that call cloud CLIs (e.g., Earth Engine / `gcloud`), prefer the notebook/web authentication fallback or a service-account workflow when running on headless systems.

