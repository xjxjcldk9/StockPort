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

TW_ETF = Path(__file__).parents[2] / 'data' / 'ETFs' / 'combined_TW.csv'


PRICE_DATA = Path(__file__).parents[2] / 'data' / 'stock_prices'
PRICE_DATA.mkdir(exist_ok=True)

PORT_DATA = Path(__file__).parents[2] / 'data' / 'portfolio'
PORT_DATA.mkdir(exist_ok=True)

parser = ArgumentParser()
parser.add_argument('case', choices=['TW', 'US'])
parser.add_argument('-s', '--scrape', action='store_true')
parser.add_argument('-v', '--value', required=True, type=int)
args = parser.parse_args()


today = datetime.today()
ym = today.strftime("%Y-%m")
prev_year = today-relativedelta(years=1)
today = today.strftime("%Y-%m-%d")
prev_year = prev_year.strftime("%Y-%m-%d")


if args.case == 'TW':
    FILE_NAME = f'TW_price_{ym}.csv'
    PRICE_FILE = PRICE_DATA / FILE_NAME
    PORT_FILE = PORT_DATA / f'TW_{ym}.csv'

elif args.case == 'US':
    FILE_NAME = f'US_price_{ym}.csv'
    PRICE_FILE = PRICE_DATA / FILE_NAME
    PORT_FILE = PORT_DATA / f'US_{ym}.csv'


def get_price(stock_name, market, start_date, end_date):
    if market == 'TW':
        tick = str(stock_name['代碼']) + '.TW'
    stock = yf.Ticker(tick)

    stock_data = stock.history(start=start_date, end=end_date)

    prices = stock_data['Close']
    return prices


def get_all_price(market):
    if market == 'TW':
        df = pd.read_csv(TW_ETF)
    if market == 'US':
        df = '../data/ETFs/combined_TW.csv'

    price_df = df.apply(get_price, 1, args=(market, prev_year, today))
    price_df = price_df.set_index(df['股票名稱'])

    return price_df.T


def optimal_portfolio(price_df, value):
    mu = mean_historical_return(price_df)
    S = CovarianceShrinkage(price_df).ledoit_wolf()

    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg, gamma=0.1)
    w = ef.max_sharpe()

    latest_prices = get_latest_prices(df)
    da = DiscreteAllocation(w, latest_prices, total_portfolio_value=value)
    allocation, leftover = da.lp_portfolio()
    return pd.Series(allocation).to_frame().reset_index().rename(columns={'index': '股票名稱', 0: '推薦購買股數'})


if __name__ == '__main__':
    if args.scrape:
        get_all_price(args.case).to_csv(PRICE_FILE)
    try:
        df = pd.read_csv(PRICE_FILE, index_col='Date')
    except FileNotFoundError:
        print(
            f'Price file {FILE_NAME} does not found. Please scrape it first.')

    portfolio_df = optimal_portfolio(df, args.value)
    portfolio_df.to_csv(PORT_FILE)
