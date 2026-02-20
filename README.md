# dnrec-dpr-revex-engine
Delaware State Parks automated revenue and expense ETL and analysis using the Polars and Socrata Open Data API

## Configuration in config.yaml
- By default, data will only download if dataset on data.delaware.gov is newer. To change, set `force_refresh` to `True`.
- Adjust results limit by setting `limit`. Low limit recommended for testing. Use `force_refresh` after raising limit.
