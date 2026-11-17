# Nairobi urban heat islands: ward-level temperature mapping

Maps land surface temperature (LST) for Nairobi's 85 wards from Landsat 9 and ranks wards by heat. My GeoNova analysis found Kawangware about **4.1 °C hotter** than the county average.

## Why it matters

Extreme heat is a growing climate risk for Nairobi, and it hits dense informal settlements with little tree cover hardest. Ward-level heat maps show county planners where greening, cool roofs and shade will reduce the most risk, and they fit directly into ward-based planning and FLLoCA climate investments.

## Method

- Converts Landsat Collection 2 Level-2 `ST_B10` to °C (`DN × 0.00341802 + 149.0 − 273.15`).
- Masks cloud, dilated cloud and cloud shadow using `QA_PIXEL` bits 1, 3 and 4.
- Rasterises ward boundaries, computes mean LST per ward, the anomaly against the county mean and a heat rank, and flags wards with less than 30% clear-sky pixels.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                # run the tests
```

```bash
PYTHONPATH=src python -m urban_heat.cli ST_B10.tif QA_PIXEL.tif nairobi_wards.gpkg --id ward
```

## Notes

LST is land surface temperature, not air temperature. It is a good indicator of heat exposure but should be combined with population and vulnerability data for risk assessment.

## Author

Kiplangat Elisha · Climate adaptation and geospatial analyst · [geonova.co.ke](https://www.geonova.co.ke)
