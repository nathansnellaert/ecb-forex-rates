import pandas as pd
import os
from pathlib import Path
from subsetsio import SubsetsClient

CURRENCY_NAMES = {
    'USD': 'United States Dollar',
    'JPY': 'Japanese Yen',
    'BGN': 'Bulgarian Lev',
    'CZK': 'Czech Koruna',
    'DKK': 'Danish Krone',
    'GBP': 'British Pound Sterling',
    'HUF': 'Hungarian Forint',
    'PLN': 'Polish Złoty',
    'RON': 'Romanian Leu',
    'SEK': 'Swedish Krona',
    'CHF': 'Swiss Franc',
    'ISK': 'Icelandic Króna',
    'NOK': 'Norwegian Krone',
    'TRY': 'Turkish Lira',
    'AUD': 'Australian Dollar',
    'BRL': 'Brazilian Real',
    'CAD': 'Canadian Dollar',
    'CNY': 'Chinese Yuan',
    'HKD': 'Hong Kong Dollar',
    'IDR': 'Indonesian Rupiah',
    'ILS': 'Israeli New Shekel',
    'INR': 'Indian Rupee',
    'KRW': 'South Korean Won',
    'MXN': 'Mexican Peso',
    'MYR': 'Malaysian Ringgit',
    'NZD': 'New Zealand Dollar',
    'PHP': 'Philippine Peso',
    'SGD': 'Singapore Dollar',
    'THB': 'Thai Baht',
    'ZAR': 'South African Rand'
}

def generate_charts(df: pd.DataFrame) -> list:
    return [{
        "metadata": {
            "type": "line",
            "title": f"EUR/{currency} - European Central Bank Reference Rate",
            "subtitle": f"Euro to {CURRENCY_NAMES[currency]} Daily Exchange Rates",
            "description": f"Historical exchange rate data for {CURRENCY_NAMES[currency]} to Euro, sourced from the European Central Bank.",
            "icon": "https://storage.googleapis.com/subsets-public-assets/source_logos/ecb.png",
            "dataset_configs": [{"label": f"EUR/{currency}", "color": "#2563eb"}],
        },
        "tags": {
            "id": f"forex-rates-{currency.lower()}",
            "source": "ecb",
            "currency": currency,
        },
        "source": {
            "name": "European Central Bank",
            "data_provider_url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html",
            "integration_url": "https://github.com/nathansnellaert/ecb-forex-rates",
            "license": "CC BY 4.0",
        },
        "data": [[idx, val] for idx, val in df[currency].items()],
    } for currency in df.columns]

def main():
    if not (api_key := os.getenv('SUBSETS_API_KEY')):
        raise ValueError("SUBSETS_API_KEY environment variable must be set")

    data_dir = Path(os.getenv('DATA_DIR', 'data'))
    df = pd.read_csv(data_dir / 'forex_rates.csv', index_col='date')
    
    client = SubsetsClient(api_key)
    charts = generate_charts(df)
    client.sync(charts)
    print(f"Synced {len(charts)} charts")

if __name__ == '__main__':
    main()