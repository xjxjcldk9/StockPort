from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
from argparse import ArgumentParser
import warnings
warnings.filterwarnings("ignore")

TW_ETF = Path(__file__).parents[2] / 'data' / 'ETFs' / 'combined_TW.csv'


data_storage = Path(__file__).parents[2] / 'data' / 'stock_prices'
data_storage.mkdir(exist_ok=True)

SAVE_FILE_TW = data_storage / 'TW_price.csv'


parser = ArgumentParser()
parser.add_argument('case', choices=['TW', 'US'])
args = parser.parse_args()


today = datetime.today()
prev_year = today-relativedelta(years=1)
today = today.strftime("%Y-%m-%d")
prev_year = prev_year.strftime("%Y-%m-%d")


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


if __name__ == '__main__':
    get_all_price(args.case).to_csv(SAVE_FILE_TW)
