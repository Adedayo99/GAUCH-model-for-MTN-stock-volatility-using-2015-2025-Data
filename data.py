"""Module for API and SQLite database operations."""

import sqlite3
import pandas as pd
import requests
from config import config

class AlphaAPIClient:
    """Handles data retrieval from AlphaVantage API."""

    def __init__(self, api_key=config.alpha_key):
        self._api_key = api_key

    def get_daily_data(self, symbol, size='full'):
        """Fetch daily stock data for a specific symbol."""
        url = (
            "https://learn-api.wqu.edu/1/data-services/alpha-vantage/query?"
            f"function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={size}&datatype=json&apikey={self._api_key}"
        )
        resp = requests.get(url)
        data = resp.json()

        if 'Time Series (Daily)' not in data:
            raise Exception(f"Invalid symbol '{symbol}'. Check ticker.")

        timeseries = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index', dtype=float)
        timeseries.index = pd.to_datetime(timeseries.index)
        timeseries.index.name = 'date'
        timeseries.columns = [col.split('. ')[1] for col in timeseries.columns]
        return timeseries


class SQLiteHandler:
    """Handles saving and reading stock data from SQLite database."""

    def __init__(self, connection):
        self.conn = connection

    def insert_records(self, table, df, if_exists='fail'):
        """Insert a DataFrame into SQLite."""
        inserted = df.to_sql(name=table, con=self.conn, if_exists=if_exists)
        return {'status': True, 'rows_inserted': inserted}

    def fetch_records(self, table, limit=None):
        """Read data from SQLite database."""
        query = f"SELECT * FROM '{table}'" + (f" LIMIT {limit}" if limit else '')
        return pd.read_sql(sql=query, con=self.conn, index_col='date', parse_dates=['date'])
