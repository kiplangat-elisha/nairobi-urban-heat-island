"""Landsat Collection 2 Level-2 surface temperature to degrees Celsius, with cloud masking.

USGS scaling for ST_B10: LST_K = DN * 0.00341802 + 149.0 (Collection 2 Level-2).
QA_PIXEL bits used for masking: 1 dilated cloud, 3 cloud, 4 cloud shadow.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

ST_SCALE = 0.00341802
ST_OFFSET = 149.0
KELVIN_TO_C = 273.15
ST_FILL = 0
QA_DILATED_CLOUD_BIT = 1
QA_CLOUD_BIT = 3
QA_SHADOW_BIT = 4


def st_to_celsius(st_dn: npt.NDArray[np.integer]) -> npt.NDArray[np.float64]:
    """Convert ST_B10 digital numbers to °C; fill values become NaN."""
    dn = np.asarray(st_dn)
    out = dn.astype(float) * ST_SCALE + ST_OFFSET - KELVIN_TO_C
    out[dn == ST_FILL] = np.nan
    return out


def clear_mask(qa_pixel: npt.NDArray[np.integer]) -> npt.NDArray[np.bool_]:
    """True where the pixel is free of cloud, dilated cloud and cloud shadow."""
    qa = np.asarray(qa_pixel).astype(np.uint16)
    bad = 0
    for bit in (QA_DILATED_CLOUD_BIT, QA_CLOUD_BIT, QA_SHADOW_BIT):
        bad |= 1 << bit
    return (qa & bad) == 0


def masked_lst(
    st_dn: npt.NDArray[np.integer], qa_pixel: npt.NDArray[np.integer]
) -> npt.NDArray[np.float64]:
    """LST in °C with cloudy and fill pixels set to NaN."""
    if np.shape(st_dn) != np.shape(qa_pixel):
        raise ValueError("ST_B10 and QA_PIXEL must have the same shape.")
    lst = st_to_celsius(st_dn)
    lst[~clear_mask(qa_pixel)] = np.nan
    return lst
