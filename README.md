# Stock Recommender Project

## Overview

This project is based on the procedure described in [this paper](https://ieeexplore.ieee.org/document/8456121)
and aims to recommend stocks from some of the famous ETFs in Taiwan, such as 0050, 0051, and 0056.
The primary goal is to predict the stock price log return for the next two quarter.

## Features

- **Stock Selection:** The project selects the top 20% performing stocks for each industry from the ETFs.
- **Portfolio Allocation:** Utilizes PyportfolioOpt to calculate the best portfolio allocation for the selected stocks.

### Usage

1. Execute `scrape_fundamentals.py` to acquire the raw data.
2. Execute `raw_data_to_df.py` to transform the raw data into useful dataframe.
3. Execute `predict_stocks.py` to identify the most profitable stocks by industry.
4. Execute `obtain_historical_daily.py` to retrieve the one-year historical stock prices for the recommended companies.
5. Execute `form_portfolio.py` to create the optimal portfolio for this quarter.
