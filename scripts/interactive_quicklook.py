# Arctic Navigation Quicklook — Panel/hvplot App
# ------------------------------------------------
# Launch with:  panel serve app.py --autoreload --show --allow-websocket-origin=localhost:5006,localhost:5007
# (Save this file as `app.py` or similar.)

import numpy as np
import pandas as pd
import xarray as xr

import holoviews as hv
import hvplot.xarray  # noqa
import hvplot.pandas  # noqa
import panel as pn

# Optional colormaps (fallbacks if packages aren't installed)
try:
    from cmcrameri import cm as cmcr
    HAWAII = cmcr.hawaii
except Exception:  # pragma: no cover
    HAWAII = "viridis"  # use lowercase matplotlib name when falling back

try:
    from cmocean import cm as cmo
    ICE_CMAP = cmo.ice
except Exception:  # pragma: no cover
    ICE_CMAP = "Blues"

hv.extension("bokeh")
pn.extension(design="material")

# Normalize colormap values to strings to avoid hvplot's iterable check on MPL objects

def _cmap_name(c):
    """Return a string name for a cmap or pass through strings; fall back to 'viridis'."""
    try:
        if isinstance(c, str):
            return c
        # matplotlib colormap objects usually have a .name
        name = getattr(c, "name", None)
        return name or "viridis"
    except Exception:
        return "viridis"

ICE_CMAP = 'Blues_r'
HAWAII = 'viridis'

# -----------------------
# Configuration
# -----------------------
from pathlib import Path

# Prefer repo-relative paths but fall back to original ../../../ layout
CANDIDATE_DATASET_PATHS = [
    Path("data/observations/processed/bbr_BACSAM2_p6_processed.nc"),
    Path("../../../data/observations/processed/bbr_BACSAM2_p6_processed.nc"),
]
CANDIDATE_SIC_PATHS = [
    Path("data/observations/processed/satellite_unified/sic_modis-aqua_amsr2-gcom-w1_merged_nh_1000m_APRIL.nc"),
    Path("../../../data/observations/processed/satellite_unified/sic_modis-aqua_amsr2-gcom-w1_merged_nh_1000m_APRIL.nc"),
]

def _resolve_path(candidates):
    for p in candidates:
        if p.exists():
            return str(p)
    # return the first even if missing so user sees a clear error from xarray
    return str(candidates[0])

DATASET_PATH = _resolve_path(CANDIDATE_DATASET_PATHS)
SIC_PATH = _resolve_path(CANDIDATE_SIC_PATHS)

# -----------------------
# Data loading
# -----------------------
@pn.cache
def load_data():
    ds = xr.open_dataset(DATASET_PATH)
    ds_sic = xr.open_dataset(SIC_PATH).squeeze()
    ds_sic = ds_sic.where(ds_sic.sic <= 100)

    # Ensure SIC has lon/lat as coordinates with those exact names
    if "lon" not in ds_sic.coords and "lon" in ds_sic:
        ds_sic = ds_sic.assign_coords(lon=ds_sic["lon"])  # no-op if present as var
    if "lat" not in ds_sic.coords and "lat" in ds_sic:
        ds_sic = ds_sic.assign_coords(lat=ds_sic["lat"])  # no-op if present as var

    # Convenience coordinate (hour-of-day as float)
    hod = (ds.time.dt.hour * 3600 + ds.time.dt.minute * 60 + ds.time.dt.second) / 3600
    ds = ds.assign_coords(hour_of_day=("time", hod.values.astype(float)))
    return ds, ds_sic

DS, DS_SIC = load_data()

# List of available days
DAYS = np.unique(DS.time.dt.strftime("%Y-%m-%d").values).tolist()

# -----------------------
# Widgets
# -----------------------
if len(DAYS) == 0:
    raise RuntimeError("No days found in dataset — check the dataset path/time coordinate.")

w_day = pn.widgets.Select(name="Day", value=DAYS[0], options=DAYS)
w_coarsen = pn.widgets.IntSlider(name="Coarsen (time points)", value=20, start=1, end=300, step=1)
w_pointsize = pn.widgets.IntSlider(name="Marker size", value=5, start=1, end=20)
w_alpha = pn.widgets.FloatSlider(name="Alpha", value=0.9, start=0.1, end=1.0, step=0.05)
w_show_sic = pn.widgets.Checkbox(name="Show Sea Ice Concentration (daily mean)", value=True)

# Placeholder; will be updated once day is set
w_timerange = pn.widgets.DatetimeRangeSlider(name="Time Range", start=None, end=None, value=None, step=60*1000)

# -----------------------
# Helper functions
# -----------------------

def _sel_day(ds, day):
    return ds.sel(time=slice(f"{day}T00:00", f"{day}T23:59:59"))


def _prep_day(ds, day, coarsen):
    ds_day = _sel_day(ds, day)
    # coarsen along time; boundary='trim' to avoid ragged edge
    if coarsen and coarsen > 1:
        ds_day = ds_day.coarsen(time=coarsen, boundary="trim").mean()
    return ds_day


def _make_timerange(day):
    dsel = _sel_day(DS, day)
    t0 = pd.to_datetime(str(dsel.time.min().values))
    t1 = pd.to_datetime(str(dsel.time.max().values))
    # Update the slider limits and default to full day
    w_timerange.start = t0
    w_timerange.end = t1
    w_timerange.value = (t0, t1)


def _filter_timerange(ds_day, t_range):
    if not t_range or t_range[0] is None or t_range[1] is None:
        return ds_day
    return ds_day.sel(time=slice(pd.to_datetime(t_range[0]), pd.to_datetime(t_range[1])))


def _hour_ticks():
    return {i: f"{i:02d}:00" for i in range(0, 25, 1)}


# -----------------------
# Plot builders
# -----------------------

def build_timeseries(ds_day, size=5, alpha=0.9):
    """Return a Holoviews Layout of time series with shared x-axis and hover."""
    # Options must be set on *elements*, not on a Layout (HV raises on 'tools' for Layout)
    elem_opts = dict(tools=["hover", "pan", "box_zoom", "wheel_zoom", "reset"],
                     active_tools=["wheel_zoom"],
                     responsive=True)

    # Use hour_of_day for color mapping
    if "hour_of_day" not in ds_day.coords:
        hod = (ds_day.time.dt.hour * 3600 + ds_day.time.dt.minute * 60 + ds_day.time.dt.second) / 3600
        ds_day = ds_day.assign_coords(hour_of_day=("time", hod.astype(float)))

    cmap = HAWAII

    alt = ds_day.hvplot.scatter(x="time", y="altitude", c="hour_of_day", cmap=_cmap_name(cmap), clim=(0, 24),
                                size=size, alpha=alpha, colorbar=True, ylabel="Altitude (m)", frame_width=1400, frame_height=200).opts(**elem_opts)
    pitch = ds_day.hvplot.scatter(x="time", y="pitch", c="hour_of_day", cmap=_cmap_name(cmap), clim=(0, 24),
                                  size=size, alpha=alpha, colorbar=False, ylabel="Pitch (deg)", frame_width=1400, frame_height=200).opts(**elem_opts)
    roll = ds_day.hvplot.scatter(x="time", y="roll", c="hour_of_day", cmap=_cmap_name(cmap), clim=(0, 24),
                                 size=size, alpha=alpha, colorbar=False, ylabel="Roll (deg)", frame_width=1400, frame_height=200).opts(**elem_opts)
    kt19 = ds_day.hvplot.scatter(x="time", y="t_kt19", c="hour_of_day", cmap=_cmap_name(cmap), clim=(0, 24),
                                 size=size, alpha=alpha, colorbar=False, ylabel="KT19 (K)", frame_width=1400, frame_height=200).opts(**elem_opts)
    lat = ds_day.hvplot.scatter(x="time", y="latitude", c="hour_of_day", cmap=_cmap_name(cmap), clim=(0, 24),
                                size=size, alpha=alpha, colorbar=False, ylabel="Latitude (°)", frame_width=1400, frame_height=200).opts(**elem_opts)
    lon = ds_day.hvplot.scatter(x="time", y="longitude", c="hour_of_day", cmap=_cmap_name(cmap), clim=(0, 24),
                                size=size, alpha=alpha, colorbar=False, ylabel="Longitude (°)", frame_width=1400, frame_height=200  ).opts(**elem_opts)

    grid = (alt + pitch + roll + kt19 + (lat + lon)).cols(1).opts(merge_tools=False, toolbar="above")
    return grid


def build_map(ds_day, ds_sic_day_mean, size=6, alpha=0.9, show_sic=True):
    """Geographic view: optional SIC raster + colored track, both in geographic coords.
    Uses DataFrame for points to avoid xarray gridded-kdim checks.
    """
    # Convert to tidy DataFrame for points
    needed = [v for v in ["longitude", "latitude", "hour_of_day"] if v in ds_day]
    df = ds_day[needed].to_dataframe().reset_index()
    df = df.dropna(subset=[c for c in ["longitude", "latitude"] if c in df])

    pts = df.hvplot.points(x="longitude", y="latitude", c="hour_of_day", cmap=_cmap_name(HAWAII), clim=(0, 24),
                           size=size, alpha=alpha, geo=True, tiles="OSM", colorbar=True,
                           xlabel="Lon", ylabel="Lat", frame_width=700, frame_height=520)

    if show_sic and ds_sic_day_mean is not None:
        # Important: SIC quadmesh uses coords named lon/lat
        sic = ds_sic_day_mean.hvplot.quadmesh(x="lon", y="lat", rasterize=True, geo=True, tiles=None,
                                              clim=(0, 100), cmap=_cmap_name(ICE_CMAP), alpha=0.6, colorbar=True,
                                              xlabel="Lon", ylabel="Lat")
        return sic * pts
    return pts


# -----------------------
# Reactive pipeline
# -----------------------

@pn.depends(w_day.param.value, watch=True)
def _on_day_change(day):
    _make_timerange(day)


def _ds_for_view(day, coarsen, t_range):
    ds_day = _prep_day(DS, day, coarsen)
    ds_day = _filter_timerange(ds_day, t_range)
    return ds_day


@pn.depends(w_day, w_coarsen, w_timerange, w_pointsize, w_alpha, w_show_sic)
def view(day, coarsen, t_range, pointsize, alpha, show_sic):
    ds_day = _ds_for_view(day, coarsen, t_range)

    # Prepare SIC daily mean for the chosen day (independent of time range)
    ds_sic_day = DS_SIC.sic.sel(time=slice(f"{day}T00:00", f"{day}T23:59:59"))
    ds_sic_day_mean = None
    if show_sic and ds_sic_day.time.size > 0:
        ds_sic_day_mean = ds_sic_day.mean("time").to_dataset(name="sic")
        # Ensure coords are present for quadmesh
        ds_sic_day_mean = ds_sic_day_mean.assign_coords(lat=DS_SIC.lat, lon=DS_SIC.lon)

    ts = build_timeseries(ds_day, size=pointsize, alpha=alpha)
    mp = build_map(ds_day, ds_sic_day_mean, size=pointsize+1, alpha=alpha, show_sic=show_sic)

    return pn.Column(mp, ts)


# Initialize timerange for default day
_make_timerange(w_day.value)

# -----------------------
# Template / Layout
# -----------------------

header = pn.pane.Markdown(
    """
# Arctic Navigation Quicklook
Explore daily flights: select a day, then **zoom** or use the **Time Range** to focus. 
Plots are colored by *hour-of-day* and stay in sync with the map.
    """,
    sizing_mode="stretch_width",
)

controls = pn.Card(
    pn.Column(
        pn.Row(w_day, w_coarsen),
        pn.Row(w_pointsize, w_alpha),
        w_show_sic,
        w_timerange,
    ),
    title="Controls",
    collapsed=False,
)

footer = pn.pane.Markdown(
    """
*Tips*: Use the mouse wheel or box zoom on any plot. Drag the **Time Range** slider to instantly filter all views.
    """,
    sizing_mode="stretch_width",
)

app = pn.template.MaterialTemplate(
    site="Arctic Tools",
    title="Navigation Quicklook",
    header=[header],
    sidebar=[controls],
    main=[view],
    sidebar_width=380,
)

# Serveable
app.servable()
