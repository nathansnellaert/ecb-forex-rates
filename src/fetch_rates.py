from pathlib import Path
import argparse
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from typing import Dict
from requests.exceptions import RequestException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import os


AVAILABLE_CURRENCIES = {
    'USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON', 'SEK', 
    'CHF', 'ISK', 'NOK', 'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 
    'ILS', 'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP', 'SGD', 'THB', 'ZAR'
}

DATA_DIR = Path(os.getenv('DATA_DIR', 'data'))

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(RequestException)
)   
def make_request(url: str, params: Dict) -> str:
    response = requests.get(
        url, 
        headers={'Accept': 'application/xml'}, 
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.content

def fetch_currency_data(currency: str, start_date: str) -> pd.Series:
    ns = {'ns': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'}
    url = f"https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.{currency}.EUR.SP00.A"
    
    try:
        content = make_request(url, {'startPeriod': start_date})
        root = ET.fromstring(content)
        data = {}
        
        for series in root.findall('.//ns:Series', ns):
            for obs in series.findall('.//ns:Obs', ns):
                date = obs.find('.//ns:ObsDimension', ns).get('value')
                rate = float(obs.find('.//ns:ObsValue', ns).get('value'))
                data[date] = rate
                
        return pd.Series(data, name=currency)
    except (ET.ParseError, RequestException) as e:
        print(f"Warning: Failed to fetch {currency}: {str(e)}")
        return pd.Series(name=currency)

def fetch_data(start_date: str) -> pd.DataFrame:    
    series_list = []
    for currency in sorted(AVAILABLE_CURRENCIES):
        print(f"Fetching {currency} from {start_date}")
        currency_data = fetch_currency_data(currency, start_date)
        series_list.append(currency_data)
    
    df = pd.concat(series_list, axis=1)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'date'
    return df.sort_index()

def main(start_date: str) -> bool:
    if not start_date:
        raise ValueError("START_DATE must be provided")

    DATA_DIR.mkdir(exist_ok=True)
    forex_file = DATA_DIR / 'forex_rates.csv'

    if forex_file.exists():
        existing_df = pd.read_csv(forex_file, index_col='date', parse_dates=['date'])
        latest_date = existing_df.index.max().strftime('%Y-%m-%d')
        fetch_start_date = latest_date
    else:
        existing_df = None
        fetch_start_date = start_date

    print(f"Fetching forex data from {fetch_start_date}")
    new_df = fetch_data(fetch_start_date)
    
    if new_df is None or new_df.empty:
        print("No new data available")
        return False

    if existing_df is not None:
        df = pd.concat([existing_df, new_df])
        df = df[~df.index.duplicated(keep='last')]
        df = df.sort_index()
    else:
        df = new_df
    
    df.to_csv(forex_file)
    print(f"Data saved to {forex_file}")
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} currencies")
    print(f"Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch ECB forex data')
    parser.add_argument('--start-date', type=str, required=True, 
                       help='Earliest date to fetch data from (YYYY-MM-DD)')
    
    args = parser.parse_args()
    success = main(
        start_date=args.start_date
    )
    exit(0 if success else 1)