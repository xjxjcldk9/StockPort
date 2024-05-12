import json
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd
from config import ETF_PATH, DATA_PATH
import datetime
from pathlib import Path

# selenium setting
options = Options()
options.page_load_strategy = 'normal'
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--enable-javascript")
options.add_argument("--headless=new")


df_0050s = pd.read_csv(ETF_PATH+'/0050.csv')
df_tw100s = pd.read_csv(ETF_PATH+'/tw100.csv')
df_0056s = pd.read_csv(ETF_PATH+'/0056.csv')

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


domain_name = "https://www.wantgoo.com/stock"

time = datetime.datetime.now()
date = time.strftime("%Y_%m")


file_storage_path = f"{DATA_PATH}/{date}_raw"
Path(file_storage_path).mkdir(exist_ok=True)

driver = webdriver.Chrome(options=options)


def scraping(tick):
    tick_table = {}
    try:
        for feature in stock_features:
            url = f"{domain_name}/{tick}/{stock_features[feature]}"
            driver.get(url)
            table = driver.find_element(by=By.CSS_SELECTOR, value='table')
            wait = WebDriverWait(driver, timeout=20)
            wait.until(lambda _: table.is_displayed())
            tick_table[feature] = table.text.split('\n')

        with open(f"{file_storage_path}/{tick}.json", "w") as f:
            json.dump(tick_table, f)
    except:
        # consider error log
        print(f"Error occurred at {tick}!")


if __name__ == '__main__':
    for i, tick in enumerate(dfs['代碼']):
        if i > 5:
            break
        scraping(tick)
