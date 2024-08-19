import ssl

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

ssl._create_default_https_context = ssl._create_unverified_context

# selenium options
options = Options()
options.page_load_strategy = 'normal'
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--enable-javascript")


# 0050股票
def get_0050_stocks():
    dfs = pd.read_html(
        'http://www.moneydj.com/ETF/X/Basic/Basic0007a.xdjhtm?etfid=0050.TW')
    stock_names = pd.concat((dfs[2], dfs[3]))[['股票名稱']].reset_index(drop=True)
    return stock_names


# 0056
def get_0056_stocks():
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.cmoney.tw/etf/tw/0056/fundholding')
    table = driver.find_element(
        by=By.CSS_SELECTOR, value='table.cm-table__table')

    wait = WebDriverWait(driver, timeout=2)
    wait.until(lambda d: table.is_displayed())

    table_list = table.text.split('\n')

    names = [table_list[i] for i in range(6, len(table_list), 4)]
    final_names = pd.DataFrame({'股票名稱': names})
    return final_names


# 臺灣100股票
def get_tw100_stocks():
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.wantgoo.com/index/%5E543/stocks')
    table = driver.find_element(by=By.CSS_SELECTOR, value='table')

    wait = WebDriverWait(driver, timeout=2)
    wait.until(lambda d: table.is_displayed())

    table_list = table.text.split('\n')
    names = [table_list[i] for i in range(1, len(table_list)-1, 3)]
    return pd.DataFrame(names)


def get_0050_stocks_ticks_industries():
    stock_tick = pd.read_csv('stock_tick.csv')
    stock_names = get_0050_stocks()
    stock_names.set_index('股票名稱').join(stock_tick.set_index(
        '名稱')).reset_index().to_csv('0050.csv', index=False)


def get_tw100_stocks_ticks_industries():
    stock_tick = pd.read_csv('stock_tick.csv')
    stock_names = get_tw100_stocks()
    stock_names = stock_names.set_index(0).join(
        stock_tick.set_index('名稱'), how='inner').reset_index()
    stock_names = stock_names.rename(columns={'index': '股票名稱'})
    stock_names.to_csv('tw100.csv', index=False)


def get_0056_stocks_ticks_industries():
    stock_tick = pd.read_csv('stock_tick.csv')
    stock_names = get_0056_stocks()
    stock_names = stock_names.set_index('股票名稱').join(stock_tick.set_index(
        '名稱'), how='inner').reset_index()
    stock_names = stock_names.rename(columns={'index': '股票名稱'})
    stock_names.to_csv('0056.csv', index=False)


def get_all_stock_ticks_industries():
    df = pd.read_excel('2023Q1.XLS', usecols='A,B', skiprows=5)
    df.columns = ['ticks', 'name']
    data = []
    for index, row in df.iterrows():
        if pd.isna(row['name']):
            flag = True
            continue
        if flag == True:
            industry = row['name']
            flag = False
            continue

        if not pd.isna(row['ticks']):
            data.append((row['ticks'], row['name'], industry))
    final_df = pd.DataFrame(data, columns=['代碼', '名稱', '產業'])
    final_df['代碼'] = final_df['代碼'].astype('int').astype('object')
    final_df.to_csv('stock_tick.csv', index=False)
