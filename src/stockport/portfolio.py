import pandas as pd
import yfinance as yf
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt import objective_functions

from pathlib import Path


def get_price(tick, period) -> pd.DataFrame:
    stock = yf.Tickers(tick)
    stock_data = stock.history(period=period)

    prices = stock_data['Close']
    return prices


def get_all_prices(market, period):
    ticks_dir = Path(__file__).parent / 'static_information'
    df = pd.read_csv(ticks_dir / f'{market}.csv', dtype={'Symbol': str})

    if market == 'TW':
        df['Symbol'] = df['Symbol'] + '.TW'
    ticks = ' '.join(df['Symbol'])
    prices = get_price(ticks, period)

    return prices


def optimal_portfolio(price_df, value):
    mu = mean_historical_return(price_df)
    S = CovarianceShrinkage(price_df).ledoit_wolf()

    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg, gamma=0.2)
    w = ef.max_sharpe()

    weights = pd.Series(w)
    #只留下前五個
    my_weight = weights.sort_values(ascending=False)[:5]
    my_weight /= my_weight.sum()

    # latest_prices = get_latest_prices(price_df)
    # da = DiscreteAllocation(w, latest_prices, total_portfolio_value=value)
    # allocation, leftover = da.lp_portfolio()

    # return pd.DataFrame({
    #     'price': latest_prices,
    #     'units': pd.Series(allocation)
    # }).dropna()


def process_portfolio(portfolio_df, data):
    stock_tick = pd.read_csv(data, index_col='名稱')
    portfolio_df = portfolio_df.join(stock_tick).reset_index(names='Name')
    portfolio_df = portfolio_df.sort_values('units', ascending=False)
    return portfolio_df
