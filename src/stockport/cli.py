import typer

from .portfolio import get_all_prices, optimal_portfolio

app = typer.Typer()


@app.command()
def buy(market: str, value: int, period: str = '3mo'):
    df = get_all_prices(market, period)

    df = df.drop(columns=df.columns[df.isnull().any()])
    opt_df_weight = optimal_portfolio(df)

    opt_df = opt_df_weight * value
    print(opt_df)
    opt_df.to_csv('opt_port.csv')
