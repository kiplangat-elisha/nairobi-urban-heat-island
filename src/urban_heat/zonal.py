"""Ward-level mean LST, anomaly against the county mean, and heat ranking."""

from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from affine import Affine
from rasterio.features import rasterize

MIN_VALID_SHARE = 0.3  # wards with less clear-sky coverage than this are flagged


def ward_heat_table(
    lst: np.ndarray,
    transform: Affine,
    wards: gpd.GeoDataFrame,
    raster_crs: str,
    id_col: str = "ward",
) -> pd.DataFrame:
    """Mean LST per ward and its difference from the area-wide mean.

    Args:
        lst: 2-D LST array in °C (NaN = no data).
        transform: Affine transform of the raster.
        wards: Ward polygons; reprojected to ``raster_crs`` if needed.
        raster_crs: CRS of the LST raster.
        id_col: Column with the ward name.

    Returns:
        One row per ward with mean °C, anomaly °C, rank (1 = hottest) and a flag
        for low clear-sky coverage.
    """
    if wards.empty:
        raise ValueError("wards is empty.")
    w = wards.to_crs(raster_crs).reset_index(drop=True)
    zones = rasterize(
        ((geom, i + 1) for i, geom in enumerate(w.geometry)),
        out_shape=lst.shape,
        transform=transform,
        fill=0,
        dtype="int32",
    )
    county_mean = float(np.nanmean(lst[zones > 0]))
    rows = []
    for i, name in enumerate(w[id_col]):
        cells = lst[zones == i + 1]
        valid = cells[~np.isnan(cells)]
        share = valid.size / cells.size if cells.size else 0.0
        mean = float(valid.mean()) if valid.size else np.nan
        rows.append({id_col: name, "mean_lst_c": mean, "valid_share": share})
    out = pd.DataFrame(rows)
    out["anomaly_c"] = out["mean_lst_c"] - county_mean
    out["low_coverage"] = out["valid_share"] < MIN_VALID_SHARE
    out["heat_rank"] = out["mean_lst_c"].rank(ascending=False, method="min").astype("Int64")
    return out.sort_values("heat_rank").reset_index(drop=True)
