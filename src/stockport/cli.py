from enum import Enum

import typer

from .portfolio import get_all_prices, optimal_portfolio

app = typer.Typer()


class Market(str, Enum):
    US = 'US'
    TW = 'TW'


@app.command()
def buy(market: Market, value: int, period: str = '3mo'):
    df = get_all_prices(market.value, period)

    df = df.drop(columns=df.columns[df.isnull().any()])
    opt_df_weight = optimal_portfolio(df)

    opt_df = opt_df_weight * value
    print(opt_df)
    opt_df.to_csv('opt_port.csv')
