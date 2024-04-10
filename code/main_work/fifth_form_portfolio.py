import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices


def form_portfolio(budget):
    df = pd.read_csv('../data/recommended_stocks/stock_prices.csv',
                     parse_dates=True, index_col='Date')
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    # Optimize for maximal Sharpe ratio
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    latest_prices = get_latest_prices(df)
    da = DiscreteAllocation(cleaned_weights, latest_prices,
                            total_portfolio_value=budget)
    allocation, leftover = da.greedy_portfolio()
    print("Discrete allocation:", allocation)
    print("Funds remaining: ${:.2f}".format(leftover))


form_portfolio(100_000)
