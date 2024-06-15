import json
import pandas as pd
import numpy as np
import yfinance as yf
from config import STOCK_TICK_PATH, DATA_PATH
import datetime
from pathlib import Path
import os


stock_tick = pd.read_csv(STOCK_TICK_PATH+'/stock_tick.csv')


time = datetime.datetime.now()
date = time.strftime("%Y_%m")

file_storage_path = f"{DATA_PATH}/{date}"


def deal_month_freq(fundamental):

    dfs = []
    for feature in ['P/E Ratio', '股價淨值比(P/B)']:
        df_string = fundamental[feature]

        df = pd.DataFrame([row.split()[:-1] for row in df_string[1:]],
                          columns=df_string[0].split()[:-1])

        name = df.columns[1]
        df['年度/月份'] = pd.to_datetime(df['年度/月份'], format='%Y/%m')

        df[name] = pd.to_numeric(df[name])
        df = df.groupby(pd.PeriodIndex(df['年度/月份'], freq='Q')).mean()[[name]]

        df = df.reset_index()
        df = df.rename(columns={'年度/月份': '年度/季別'})
        dfs.append(df)

    df = dfs[0].set_index('年度/季別').join(dfs[1].set_index('年度/季別'))

    return df


def deal_eps(fundamental):
    df_string = fundamental['每股盈餘(EPS)']

    data = []
    for row in df_string[1:]:
        adding = row.split()
        if len(adding) > 2:
            data.append([adding[0]+adding[1], *adding[2:]])

    df = pd.DataFrame(data, columns=df_string[0].split())
    df = df.set_index(pd.PeriodIndex(df['年度/季別'], freq='Q'))
    df = df.drop(columns='年度/季別')

    df['每股盈餘'] = pd.to_numeric(df['每股盈餘'])
    # 處理季增率問題
    eps_growth_Q = pd.DataFrame.pct_change(
        df['每股盈餘'], periods=-1, fill_method=None)

    eps_growth_Y = pd.DataFrame.pct_change(
        df['每股盈餘'], periods=-4, fill_method=None)

    df = df.join(eps_growth_Q, rsuffix='季增率')
    df = df.join(eps_growth_Y, rsuffix='年增率')

    default_Q_growth = pd.to_numeric(
        df['季增率'].str.split('%').str[0], errors='coerce')*0.01
    default_Y_growth = pd.to_numeric(
        df['年增率'].str.split('%').str[0], errors='coerce')*0.01

    df['每股盈餘季增率'] = df['每股盈餘季增率'].fillna(default_Q_growth)
    df['每股盈餘年增率'] = df['每股盈餘年增率'].fillna(default_Y_growth)

    df = df.drop(columns=['季增率', '年增率'])

    return df


def deal_nwps(fundamental):
    df_string = fundamental['每股淨值']
    data = []
    for row in df_string[1:]:
        adding = row.split()[:-1]
        data.append([adding[0]+adding[1], *adding[2:]])

    df = pd.DataFrame(data, columns=df_string[0].split()[:-1])
    df = df.set_index(pd.PeriodIndex(df['年度/季別'], freq='Q'))
    df = df.drop(columns='年度/季別')
    return df


def deal_normal(fundamental):
    normal_features = ['現金比例', '營業現金對淨利', '負債佔資產比', '長期資金佔固定資產比', '流動比',
                       '週轉天', 'ROE-ROA', '財報三率', '營業利益增率']
    for i, feature in enumerate(normal_features):

        df_string = fundamental[feature]

        if ('季收盤價' in df_string[0]) and (i != 1):
            df = pd.DataFrame([row.split()[:-1] for row in df_string[1:]],
                              columns=df_string[0].split()[:-1])
        else:
            df = pd.DataFrame([row.split() for row in df_string[1:]],
                              columns=df_string[0].split())
        df = df.set_index(pd.PeriodIndex(df['年度/季別'], freq='Q'))

        df = df.drop(columns='年度/季別')

        if i == 0:
            main_df = df
        else:
            main_df = main_df.join(df)
    main_df['季收盤價'] = pd.to_numeric(main_df['季收盤價'])
    main_df['季收盤價成長率y'] = np.log(
        main_df['季收盤價'].shift(2) / main_df['季收盤價'].shift(1))
    # leakage
    # main_df = main_df.drop(columns='季收盤價')
    return main_df


# TODO: Change this
def append_last_price(df, tick):

    stock = yf.Ticker(str(tick)+'.TW')
    stock_data = stock.history()
    now_price = stock_data.sort_index(ascending=False).iloc[0]['Close']
    indices = df[df['代碼'] == tick].index
    last_price = df.loc[indices[0], '季收盤價']

    df.loc[indices[1], "季收盤價成長率y"] = np.log(now_price / last_price)


def pack_to_df(tick, fundamental):
    try:
        d1 = deal_normal(fundamental)
        d2 = deal_eps(fundamental)
        d3 = deal_nwps(fundamental)
        d4 = deal_month_freq(fundamental)
        df = d1.join(d2).join(d3).join(d4)

        specific_stock = stock_tick[stock_tick['代碼'] == int(tick)]

        df['代碼'] = tick
        df['股票名稱'] = specific_stock['名稱'].iloc[0]
        df['產業'] = specific_stock['產業'].iloc[0]

        # append_last_price(df)
    except:
        print(f'{tick} has problem!!')
    return df


def raw_to_df(raw_tables):

    dfs = []

    final_df = pd.concat(dfs)
    return final_df


if __name__ == '__main__':
    for file in os.listdir(file_storage_path+'/raw'):
        tick = file.split('.')[0]
        with open(file_storage_path+'/raw/'+file) as f:
            fundamental = json.load(f)
        pack_to_df(tick, fundamental).to_csv('test.csv')

        break
