import json
from selenium.webdriver.support.wait import WebDriverWait
from collections import defaultdict


from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd


options = Options()
options.page_load_strategy = 'normal'
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--enable-javascript")

ETF_PATH = '../data/ETFs/'
df_0050s = pd.read_csv(ETF_PATH+'0050.csv')
df_tw100s = pd.read_csv(ETF_PATH+'tw100.csv')
df_0056s = pd.read_csv(ETF_PATH+'0056.csv')

dfs = pd.concat([df_0050s, df_tw100s, df_0056s])
dfs = dfs.drop_duplicates('代碼')


stock_features = {'現金比例': 'financial-security/cash-flows-analysis',
                  '營業現金對淨利': 'profitability/operating-cash-flow-to-net-operating-profit-margin',
                  '負債佔資產比': 'financial-security/debts-ratio',
                  '長期資金佔固定資產比': 'financial-security/long-term-funds-to-fixed-assets',
                  '流動比': 'financial-security/current-quick-ratio',
                  '週轉天': 'operation-efficiency/turnover-in-days',
                  'ROE-ROA': 'profitability/ROE-ROA',
                  '財報三率': 'profitability/profit-margin',
                  '每股淨值': 'financial-statements/net-worth-per-share',
                  '營業利益增率': 'enterprise-growth/operating-profit-margin',
                  '每股盈餘(EPS)': 'financial-statements/eps',
                  '股價淨值比(P/B)': 'enterprise-value/price-book-ratio',
                  'P/E Ratio': 'enterprise-value/price-to-earning-ratio'}


# df = pd.read_csv('problems.csv')


def scraping(full_table):
    for tick in ['6550']:
        for feature in stock_features:
            try:
                driver = webdriver.Chrome(options=options)
                url = f"https://www.wantgoo.com/stock/{
                    tick}/{stock_features[feature]}"
                driver.get(url)

                table = driver.find_element(by=By.CSS_SELECTOR, value='table')

                wait = WebDriverWait(driver, timeout=2)
                wait.until(lambda d: table.is_displayed())

                full_table[tick][feature] = table.text.split('\n')
                driver.close()
            except:
                continue


DATA_PATH = '../data/full_stocks_data/'


def write_data(full_table):
    with open(DATA_PATH+"raw_tables.json", "w") as outfile:
        json.dump(full_table, outfile)


full_table = defaultdict(dict)
scraping(full_table)
write_data(full_table)
