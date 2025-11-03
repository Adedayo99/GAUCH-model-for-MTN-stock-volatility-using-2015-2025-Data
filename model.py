"""GARCH modeling and forecasting logic."""

import os
from glob import glob
import joblib
import pandas as pd
from arch import arch_model
from config import config
from data import AlphaAPIClient, SQLiteHandler

class VolatilityModel:
    """Implements GARCH model training and prediction workflow."""

    def __init__(self, ticker, db_repo, refresh_data):
        self.ticker = ticker
        self.repo = db_repo
        self.refresh_data = refresh_data
        self.model_folder = config.model_path

    def prepare_data(self, n_points):
        """Retrieve and clean stock return data."""
        if self.refresh_data:
            api_client = AlphaAPIClient()
            fresh_data = api_client.get_daily_data(self.ticker)
            self.repo.insert_records(self.ticker, fresh_data, if_exists='replace')

        df = self.repo.fetch_records(self.ticker, limit=n_points + 1)
        df.sort_index(inplace=True)
        df['returns'] = df['close'].pct_change() * 100
        self.data = df['returns'].dropna()

    def train(self, p, q):
        """Fit a GARCH(p, q) model."""
        self.model = arch_model(self.data, p=p, q=q, rescale=False).fit(disp=0)

    def _format_prediction(self, prediction):
        """Format predictions to JSON-like structure."""
        start_date = prediction.index[0] + pd.DateOffset(days=1)
        forecast_dates = pd.bdate_range(start=start_date, periods=prediction.shape[1])
        forecast_index = [d.isoformat() for d in forecast_dates]
        forecast_values = prediction.values.flatten() ** 0.5
        return pd.Series(forecast_values, index=forecast_index).to_dict()

    def predict(self, horizon):
        """Generate volatility forecast."""
        forecast = self.model.forecast(horizon=horizon, reindex=False).variance
        return self._format_prediction(forecast)

    def save_model(self):
        """Serialize trained model to disk."""
        timestamp = pd.Timestamp.now().isoformat()
        file_path = os.path.join(self.model_folder, f"{timestamp}_{self.ticker}.pkl")
        joblib.dump(self.model, file_path)
        return file_path

    def load_model(self):
        """Load the latest model for given ticker."""
        pattern = os.path.join(config.model_path, f"*{self.ticker}.pkl")
        try:
            latest_model = sorted(glob(pattern))[-1]
        except IndexError:
            raise Exception(f"No saved model found for {self.ticker}.")
        self.model = joblib.load(latest_model)
        return self.model
