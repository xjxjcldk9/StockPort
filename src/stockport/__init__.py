# from datetime import datetime
# from pathlib import Path

# import numpy as np
# import pandas as pd

# from stockport.portfolio import get_all_price, optimal_portfolio

# today = datetime.today()
# ym = today.strftime("%Y-%m")

# DATA_DIR = Path('.') / 'data'
# DATA_DIR.mkdir(exist_ok=True)

# PRICE_DIR = DATA_DIR / 'stock_prices'
# PRICE_DIR.mkdir(exist_ok=True)

# PORT_DIR = DATA_DIR / 'portfolio'
# PORT_DIR.mkdir(exist_ok=True)

# def best_port(case, still_scrape, value=None):
#     TICKS_DATA = Path(__file__).parent / 'static_information' / f'{case}.csv'

#     FILE_NAME = f'{case}_{ym}.csv'
#     PRICE_FILE = PRICE_DIR / FILE_NAME

#     scrape = False

#     if PRICE_FILE.exists():
#         if still_scrape:
#             scrape = True
#     else:
#         scrape = True

#     if scrape:
#         get_all_price(case, TICKS_DATA).to_csv(PRICE_FILE)

#     PORT_FILE = PORT_DIR / FILE_NAME

#     if value:
#         df = pd.read_csv(PRICE_FILE, index_col='Date')
#         portfolio_df = optimal_portfolio(df, value)
#         np.round(portfolio_df, 1).to_csv(PORT_FILE)
