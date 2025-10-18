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
        /processed
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

