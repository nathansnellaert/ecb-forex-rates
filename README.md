# ECB Forex Rates

Collects and publishes European Central Bank foreign exchange reference rates to Subsets. The rates cover 30 currency pairs against the EUro and are published on business days around 16:00 CET.

You can explore (and download) individual charts, and many more at [subsets.io/chart?query=ecb%20forex%20rates](https://subsets.io/chart?query=ecb%20forex%20rates).

For more information about the source data, see the [ECB official docs](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html).

## Raw Data Access
The raw data is available in `data/forex_rates.csv`. To collect it yourself:
```bash
poetry install
poetry run python src/fetch_rates.py --start-date "YYYY-MM-DD"
