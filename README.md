# dnrec-dpr-revex-engine
Delaware State Parks automated revenue and expense ETL and analysis using Polars and Socrata Open Data API

## Configuration in config.yaml
- By default, data will only download if dataset on data.delaware.gov is newer. To change, set `force_refresh` to `True`.
- Adjust results limit by setting `limit`. Low limit recommended for testing. Use `force_refresh` after raising limit.

## Source metadata
- [State of Delaware Revenue](https://data.delaware.gov/Government-and-Finance/Revenue/it4a-m3yd/about_data) 
- [State of Delaware Checkbook](https://data.delaware.gov/Government-and-Finance/State-of-Delaware-Checkbook/5s6n-7hpx/about_data)
