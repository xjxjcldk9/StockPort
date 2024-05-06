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


def objective_ridge(trial):
    with mlflow.start_run(nested=True):
        # Define hyperparameters
        params = {
            "alpha": trial.suggest_float("alpha", 1e-8, 1e5, log=True),
        }

        # Train XGBoost model
        bst = Ridge().set_params(**params).fit(train_X, train_y)
        preds = bst.predict(val_X)
        error = mean_squared_error(val_y, preds)

        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_metric("mse", error)
        mlflow.log_metric("rmse", np.sqrt(error))

    return error


plt.rcParams['font.family'] = ['Heiti TC']

# For Ridge, need to generalize


def plot_feature_importance(model):
    """
    Plots feature importance for an ridge model.

    Args:
    - model: A trained ridge model

    Returns:
    - fig: The matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(18, 8))
    coeff_df = pd.DataFrame({'coef_name': model.feature_names_in_,
                             'coef': model.coef_}).sort_values('coef')
    ax.barh(coeff_df.coef_name, coeff_df.coef)
    ax.set_title('Ridge Regression Feature Coefficients')
    plt.close(fig)

    return fig
