Volatility modeling is a key concept in quantitative finance, helping investors and analysts understand market uncertainty.

This project uses:

The Alpha Vantage API to fetch real stock data.

Python and pandas for data processing.

Statsmodels / arch libraries to fit the GARCH model.

Statistical analysis and visualization to interpret model results.

The GARCH framework captures volatility clustering — periods of high or low variance — often observed in financial time series.




**Key workflow:**

Fetch historical data for MTN Group (MTNOY).

Calculate daily percentage returns.

Fit a GARCH(p, q) model to the return series.

Analyze and visualize the conditional volatility predictions.

**Output:**

Model summary statistics

Volatility plots

Forecasts for future periods
