import warnings
from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
from argparse import ArgumentParser

from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import objective_functions


warnings.filterwarnings("ignore")


parser = ArgumentParser()
parser.add_argument('case', choices=['TW', 'US'])
parser.add_argument('-s', '--scrape', action='store_true')
parser.add_argument('-v', '--value',  type=int)
args = parser.parse_args()


DATA_DIR = Path(__file__).parents[2] / 'data'


PRICE_DIR = DATA_DIR / 'stock_prices'
PRICE_DIR.mkdir(exist_ok=True)

PORT_DIR = DATA_DIR / 'portfolio'
PORT_DIR.mkdir(exist_ok=True)


today = datetime.today()
ym = today.strftime("%Y-%m")
prev_year = today-relativedelta(years=1)
today = today.strftime("%Y-%m-%d")
prev_year = prev_year.strftime("%Y-%m-%d")


TICKS_DATA = DATA_DIR / 'static_information' / f'{args.case}.csv'

FILE_NAME = f'{args.case}_{ym}.csv'
PRICE_FILE = PRICE_DIR / FILE_NAME
PORT_FILE = PORT_DIR / FILE_NAME


def get_price(stock_name, start_date, end_date):
    if args.case == 'TW':
        tick = str(stock_name['代碼']) + '.TW'
    elif args.case == 'US':
        tick = str(stock_name['Symbol'])
    stock = yf.Ticker(tick)
    stock_data = stock.history(start=start_date, end=end_date)

    prices = stock_data['Close']
    return prices


def get_all_price(ticks_data):
    df = pd.read_csv(ticks_data)
    price_df = df.apply(get_price, 1, args=(prev_year, today))
    if args.case == 'TW':
        price_df = price_df.set_index(df['股票名稱'])
    elif args.case == 'US':
        price_df = price_df.set_index(df['Symbol'])

    return price_df.T


def optimal_portfolio(price_df, value):
    mu = mean_historical_return(price_df)
    S = CovarianceShrinkage(price_df).ledoit_wolf()

    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg, gamma=1e-3)
    w = ef.max_sharpe()

    latest_prices = get_latest_prices(price_df)
    da = DiscreteAllocation(w, latest_prices, total_portfolio_value=value)
    allocation, leftover = da.lp_portfolio()

    return pd.DataFrame({'價格': latest_prices,
                         '股數': pd.Series(allocation)}).dropna()


def process_portfolio(portfolio_df):
    if args.case == 'TW':
        stock_tick = pd.read_csv(TICKS_DATA, index_col='名稱')
        portfolio_df = portfolio_df.join(stock_tick).reset_index(names='名稱')
        portfolio_df = portfolio_df.sort_values('股數', ascending=False)
        return portfolio_df


if __name__ == '__main__':
    if args.scrape:
        get_all_price(TICKS_DATA).to_csv(PRICE_FILE)

    if args.value:
        try:
            df = pd.read_csv(PRICE_FILE, index_col='Date')
        except FileNotFoundError:
            print(
                f'Price file {FILE_NAME} does not found. Please scrape it first.')

        portfolio_df = optimal_portfolio(df, args.value)
        process_portfolio(portfolio_df).to_csv(PORT_FILE, index=False)
