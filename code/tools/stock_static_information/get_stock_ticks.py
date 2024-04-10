import pandas as pd


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


get_all_stock_ticks_industries()
