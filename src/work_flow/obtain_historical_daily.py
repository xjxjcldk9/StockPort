# %%
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta

STOCK_PATH = '../data/recommended_stocks'
df = pd.read_csv(STOCK_PATH+'/predicted_stocks.csv')


def obtain_price(start_date, end_date):
    first = True
    for __, row in df.iterrows():
        stock = yf.Ticker(str(row['代碼'])+'.TW')
        stock_data = stock.history(start=start_date, end=end_date)

        if first:
            stock_price = stock_data[['Close']]
            stock_price = stock_price.rename(columns={'Close': row['股票名稱']})
            first = False
        else:
            stock_price[row['股票名稱']] = stock_data[['Close']]

    return stock_price


today = datetime.today()
prev_year = today-relativedelta(years=1)

today = today.strftime("%Y-%m-%d")
prev_year = prev_year.strftime("%Y-%m-%d")
# %%
stock_price = obtain_price(prev_year, today)

# %%
stock_price.to_csv(STOCK_PATH+'/stock_prices.csv')
