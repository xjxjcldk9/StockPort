import pandas as pd
import yfinance as yf
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage


def get_price(tick, period) -> pd.DataFrame:
    stock = yf.Tickers(tick)
    stock_data = stock.history(period=period)

    prices = stock_data['Close']
    return prices


def optimal_portfolio(price_df, value):
    mu = mean_historical_return(price_df)
    S = CovarianceShrinkage(price_df).ledoit_wolf()

    ef = EfficientFrontier(mu, S)
    # ef.add_objective(objective_functions.L2_reg, gamma=1e-5)
    w = ef.max_sharpe()

    latest_prices = get_latest_prices(price_df)
    da = DiscreteAllocation(w, latest_prices, total_portfolio_value=value)
    allocation, leftover = da.lp_portfolio()

    return pd.DataFrame({
        'price': latest_prices,
        'units': pd.Series(allocation)
    }).dropna()


def process_portfolio(portfolio_df, data):
    stock_tick = pd.read_csv(data, index_col='名稱')
    portfolio_df = portfolio_df.join(stock_tick).reset_index(names='Name')
    portfolio_df = portfolio_df.sort_values('units', ascending=False)
    return portfolio_df
