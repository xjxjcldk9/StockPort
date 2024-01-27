import json
from collections import defaultdict
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd

# selenium setting
options = Options()
options.page_load_strategy = 'normal'
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--enable-javascript")


ETF_PATH = '../data/ETFs/'
DATA_PATH = '../data/full_stocks_data/'


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


def scraping(ticks=dfs['代碼'], store_name='raw_tables.json'):
    '''
    Scrape data from the website and store the information into raw_tables.json.

    Parameters:
    - ticks: A list of ticks to scrape. Some ticks might fail during the initial scraping, so providing a custom list helps in retrying individual ticks.
    - store_name: The name to store the raw data.
    '''
    full_table = defaultdict(dict)
    error_ticks = defaultdict(list)

    # Check name changed.
    if ticks != dfs['代碼'] and store_name == 'raw_tables.json':
        raise ValueError(
            "If provide customary ticks, store_name should be renamed.")

    for tick in ticks:
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
                error_ticks[tick].append(feature)

    with open(DATA_PATH+store_name, "w") as f:
        json.dump(full_table, f)

    with open(DATA_PATH+'error_ticks.json', "w") as f:
        json.dump(error_ticks, f)
