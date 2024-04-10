import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import ParameterGrid
from sklearn.linear_model import Lasso


df = pd.read_csv('../data/full_stocks_data/stocks.csv')

# df = df.drop(columns='季收盤價')

df[['每股盈餘季增率', '每股盈餘年增率']] = np.arctan(df[['每股盈餘季增率', '每股盈餘年增率']])

df = df.replace({-99999: np.nan})

df.loc[df['營運週轉(天)'] < -2000, '營運週轉(天)'] = np.nan


times = df['年度/季別'].unique()

test_times = times[0]
val_times = times[2:6]
train_times = times[6:21]


class zeroEstimator():
    def __init__(self):
        pass

    def fit(self, X, y):
        pass

    def predict(self, y):
        return np.zeros(len(y))


class industries:
    def __init__(self, industry):
        self.industry = industry
        self.model_errors = pd.DataFrame()
        self.predicted_returns = pd.DataFrame()

        tmp_df = df[df['產業'] == industry].drop(columns='產業')

        # drop column is missing value > 0.05
        missing_columns = tmp_df.columns[(tmp_df.isna().mean() > 0.05)
                                         & (tmp_df.columns != '季收盤價成長率y')]

        tmp_df = tmp_df.drop(columns=missing_columns)

        # 把missing的資料都丟掉
        tmp_df = tmp_df.dropna(subset=tmp_df.drop(columns='季收盤價成長率y').columns)

        self.train_X = tmp_df[tmp_df['年度/季別'].isin(
            train_times)].drop(columns=['年度/季別', '股票名稱', '代碼'])

        self.train_y = self.train_X.pop('季收盤價成長率y')

        self.val_X = tmp_df[tmp_df['年度/季別'].isin(val_times)
                            ].drop(columns=['年度/季別', '股票名稱', '代碼'])

        self.val_y = self.val_X.pop('季收盤價成長率y')

        self.test_X = tmp_df[tmp_df['年度/季別'] ==
                             test_times].drop(columns=['年度/季別', '股票名稱', '代碼', '季收盤價成長率y'])

        Ridge_grid = ParameterGrid(
            {'alpha': np.float_power(2, np.arange(-5, 5))})

        Lasso_grid = ParameterGrid(
            {'alpha': np.float_power(2, np.arange(-5, 5))})

        Lasso_grid = ParameterGrid(
            {'alpha': np.float_power(2, np.arange(-5, 5))})

        self.models = {'linear': [LinearRegression()],
                       'Ridge': [Ridge(**params) for params in Ridge_grid],
                       'Lasso': [Lasso(**params) for params in Lasso_grid],
                       'RF': [RandomForestRegressor(max_depth=10, n_estimators=50)],
                       'SVM': [SVR()],
                       'GBM': [GradientBoostingRegressor(learning_rate=0.01)],
                       'zero': [zeroEstimator()]}

    def data_preprocess(self):
        # Scaling

        means = self.train_X.mean()
        stds = self.train_X.std()

        self.train_X = (self.train_X - means) / stds
        self.val_X = (self.val_X - means) / stds
        self.test_X = (self.test_X - means) / stds

    def MSE_models(self):
        for name, models in self.models.items():
            for i, model in enumerate(models):
                model.fit(self.train_X, self.train_y)

                y_pred = model.predict(self.val_X)
                self.model_errors[name + '_' + str(i)] = pd.Series(
                    mean_squared_error(self.val_y, y_pred))

    def prediction(self):
        model_name_i = self.model_errors.columns[np.argmin(self.model_errors)]
        model_name, i = tuple(model_name_i.split('_'))
        model = self.models[model_name][int(i)]
        print(model)
        self.predicted_returns['預測成長率'] = model.predict(self.test_X)

        # 旁邊附上他的股票名稱
        origin_df = df[(df['年度/季別'] == test_times) & (df['產業'] ==
                                                      self.industry)].reset_index(drop=True)[['股票名稱', '產業', '代碼']]
        self.predicted_returns = self.predicted_returns.join(origin_df)

        self.predicted_returns = self.predicted_returns.sort_values(
            '預測成長率', ascending=False)


def predict_stocks():
    for i, industry in enumerate(df['產業'].unique()):
        s = industries(industry)
        if len(s.train_X) < 20:
            break
        # s.data_preprocess()

        print(industry)
        s.MSE_models()

        s.prediction()

        print(np.round((s.model_errors), 3))

        industry_prediction = s.predicted_returns.iloc[:len(
            s.predicted_returns) // 5]
        if i == 0:
            prediction_stocks = industry_prediction
        else:
            prediction_stocks = pd.concat(
                [prediction_stocks, industry_prediction])

    prediction_stocks.sort_values('預測成長率', ascending=False).to_csv(
        '../data/recommended_stocks/predicted_stocks.csv', index=False)


if __name__ == '__main__':
    predict_stocks()
