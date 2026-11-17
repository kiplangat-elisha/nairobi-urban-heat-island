"""Ward heat ranking from a Landsat Level-2 scene.

Run: PYTHONPATH=src python -m urban_heat.cli ST_B10.tif QA_PIXEL.tif wards.gpkg --id ward
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import rasterio

from urban_heat.lst import masked_lst
from urban_heat.zonal import ward_heat_table


def main(argv: list[str] | None = None) -> None:
    """Write a ward heat table (CSV) and print the ten hottest wards."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("st_b10", type=Path)
    p.add_argument("qa_pixel", type=Path)
    p.add_argument("wards", type=Path)
    p.add_argument("--id", default="ward")
    p.add_argument("--out", type=Path, default=Path("outputs/ward_heat.csv"))
    a = p.parse_args(argv)
    with rasterio.open(a.st_b10) as st, rasterio.open(a.qa_pixel) as qa:
        lst = masked_lst(st.read(1), qa.read(1))
        transform, crs = st.transform, st.crs.to_string()
    table = ward_heat_table(lst, transform, gpd.read_file(a.wards), crs, a.id)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(a.out, index=False, encoding="utf-8")
    print(table.head(10).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
