import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
from argparse import ArgumentParser
import warnings
warnings.filterwarnings("ignore")


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
    return stock_data[['Close']]


def get_all_price(market):
    if market == 'TW':
        df = pd.read_csv(
            '/Users/liaoshenxun/APPdevelopment/Stock Recommendation Project/data/ETFs/combined_TW.csv')
    if market == 'US':
        df = '../data/ETFs/combined_TW.csv'

    return df.apply(get_price, 1, args=(market, prev_year, today))


if __name__ == '__main__':

    get_all_price(args.case).to_csv(
        '/Users/liaoshenxun/APPdevelopment/Stock Recommendation Project/code/direct_portfolio_evaluation/test.csv', index=False)
