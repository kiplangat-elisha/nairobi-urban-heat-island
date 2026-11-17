import geopandas as gpd
import numpy as np
import pytest
from rasterio.transform import from_origin
from shapely.geometry import box

from urban_heat.lst import clear_mask, masked_lst, st_to_celsius
from urban_heat.zonal import ward_heat_table

CRS = "EPSG:32737"


def test_scaling_known_value():
    dn = np.array([44000])
    assert st_to_celsius(dn)[0] == pytest.approx(44000 * 0.00341802 + 149.0 - 273.15)


def test_fill_is_nan():
    assert np.isnan(st_to_celsius(np.array([0]))[0])


def test_cloud_bits():
    qa = np.array([0, 1 << 3, 1 << 4, 1 << 1, 1 << 6])
    assert clear_mask(qa).tolist() == [True, False, False, False, True]


def test_masked_shape_mismatch():
    with pytest.raises(ValueError):
        masked_lst(np.ones((2, 2)), np.ones((3, 3)))


def test_ward_table_ranks_and_anomaly():
    lst = np.array([[30.0, 30.0, 20.0, 20.0], [30.0, 30.0, 20.0, np.nan]])
    tr = from_origin(0, 2, 1, 1)
    wards = gpd.GeoDataFrame({"ward": ["Hot", "Cool"]},
                             geometry=[box(0, 0, 2, 2), box(2, 0, 4, 2)], crs=CRS)
    out = ward_heat_table(lst, tr, wards, CRS).set_index("ward")
    assert out.loc["Hot", "heat_rank"] == 1
    assert out.loc["Hot", "mean_lst_c"] == pytest.approx(30.0)
    assert out.loc["Cool", "valid_share"] == pytest.approx(0.75)
    assert out.loc["Hot", "anomaly_c"] > 0 > out.loc["Cool", "anomaly_c"]


def test_empty_wards():
    with pytest.raises(ValueError):
        ward_heat_table(np.ones((2, 2)), from_origin(0, 2, 1, 1),
                        gpd.GeoDataFrame({"ward": []}, geometry=[], crs=CRS), CRS)
