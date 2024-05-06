import pandas as pd
import numpy as np
import mlflow
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR
from mlflow.models import infer_signature
from mlflow.models import MetricThreshold
import optuna
import matplotlib.pyplot as plt


df = pd.read_csv('../data/full_stocks_data/stocks.csv',
                 index_col=['產業', '年度/季別', '股票名稱', '代碼'])


df[['每股盈餘季增率', '每股盈餘年增率']] = np.arctan(df[['每股盈餘季增率', '每股盈餘年增率']])

df = df.replace({-99999: np.nan})

df.loc[df['營運週轉(天)'] < -2000, '營運週轉(天)'] = np.nan


times = df.reset_index('年度/季別')['年度/季別'].unique()

test_times = times[0]
val_times = times[2:6]
train_times = times[6:21]


def train_test_split(df, industry):
    '''
    split by industry
    '''
    focus_df = df.loc[industry]
    y = '季收盤價成長率y'

    missing_columns = focus_df.columns[(focus_df.isna().mean() > 0.05)
                                       & (focus_df.columns != y)]

    focus_df = focus_df.drop(columns=missing_columns)
    focus_df = focus_df.dropna(subset=focus_df.drop(columns=y).columns)

    train_X = focus_df.loc[train_times]
    train_y = train_X.pop(y)

    val_X = focus_df.loc[val_times]
    val_y = val_X.pop(y)

    test_X = focus_df.loc[test_times]
    test_y = test_X.pop(y)

    return train_X, train_y, val_X, val_y, test_X, test_y


def get_or_create_experiment(experiment_name):
    """
    Retrieve the ID of an existing MLflow experiment or create a new one if it doesn't exist.

    This function checks if an experiment with the given name exists within MLflow.
    If it does, the function returns its ID. If not, it creates a new experiment
    with the provided name and returns its ID.

    Parameters:
    - experiment_name (str): Name of the MLflow experiment.

    Returns:
    - str: ID of the existing or newly created MLflow experiment.
    """

    if experiment := mlflow.get_experiment_by_name(experiment_name):
        return experiment.experiment_id
    else:
        return mlflow.create_experiment(experiment_name)


# override Optuna's default logging to ERROR only
optuna.logging.set_verbosity(optuna.logging.ERROR)

# define a logging callback that will report on only new challenger parameter configurations if a
# trial has usurped the state of 'best conditions'


def champion_callback(study, frozen_trial):
    """
    Logging callback that will report when a new trial iteration improves upon existing
    best trial values.
    """

    winner = study.user_attrs.get("winner", None)

    if study.best_value and winner != study.best_value:
        study.set_user_attr("winner", study.best_value)
        if winner:
            improvement_percent = (
                abs(winner - study.best_value) / study.best_value) * 100
            print(
                f"Trial {frozen_trial.number} achieved value: {
                    frozen_trial.value} with "
                f"{improvement_percent: .4f}% improvement"
            )
        else:
            print(f"Initial trial {frozen_trial.number} achieved value: {
                  frozen_trial.value}")


# Initiate the parent run and call the hyperparameter tuning child run logic
def mlflow_run(experiment_id, run_name, model_type):
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name, nested=True):
        # Initialize the Optuna study
        study = optuna.create_study(direction="minimize")

        # Execute the hyperparameter optimization trials.
        # Note the addition of the `champion_callback` inclusion to control our logging
        # collect all objectives in a helper file, according to model_type import
        study.optimize(..., n_trials=500,
                       callbacks=[champion_callback])

        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_mse", study.best_value)
        mlflow.log_metric("best_rmse", np.sqrt(study.best_value))

        # Log a fit model instance
        model = Ridge().set_params(**study.best_params).fit(train_X, train_y)

        # Log the correlation plot
        # mlflow.log_figure(figure=correlation_plot,
        #                  artifact_file="correlation_plot.png")

        # Log the feature importances plot
        importances = plot_feature_importance(model)
        mlflow.log_figure(figure=importances,
                          artifact_file="feature_importances.png")

        # Log the residuals plot
        # residuals = plot_residuals(model, dvalid, valid_y)
        # mlflow.log_figure(figure=residuals, artifact_file="residuals.png")

        artifact_path = "model"

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=artifact_path,
            input_example=train_X.iloc[[0]],
            metadata={"model_data_version": 1},
        )

        # Get the logged model uri so that we can load it from the artifact store
        # model_uri = mlflow.get_artifact_uri(artifact_path)
