"""
model_ml.py — XGBoost regression model on engineered features (see features.py).

This reframes forecasting as supervised regression: given calendar features,
lag features, and rolling statistics at time T, predict load_mw at time T.

Why XGBoost: handles non-linear feature interactions (e.g. "hour x is_weekend"
interactions) without manual specification, trains fast, and is the standard
strong-baseline choice for tabular forecasting problems in industry.
"""

import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

TARGET_COL = "load_mw"


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """All columns except the target and any raw calendar columns already
    superseded by their cyclical (sin/cos) encodings."""
    exclude = {TARGET_COL, "hour", "day_of_week"}  # superseded by sin/cos versions
    return [c for c in df.columns if c not in exclude]


def train_xgboost(train_df: pd.DataFrame) -> xgb.XGBRegressor:
    feature_cols = get_feature_columns(train_df)
    X_train = train_df[feature_cols]
    y_train = train_df[TARGET_COL]

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def forecast_xgboost(model: xgb.XGBRegressor, test_df: pd.DataFrame) -> pd.Series:
    feature_cols = get_feature_columns(test_df)
    X_test = test_df[feature_cols]
    preds = model.predict(X_test)
    return pd.Series(preds, index=test_df.index)


def feature_importance(model: xgb.XGBRegressor, train_df: pd.DataFrame) -> pd.Series:
    """Useful for interview discussion: which features actually drive the
    model's predictions? Often lag_96 (yesterday, same time) and lag_672
    (last week, same time) dominate, which is itself an interesting finding —
    it suggests the ML model is mostly rediscovering what the naive seasonal
    baseline already encodes, plus smaller corrections from calendar/rolling
    features. Worth checking and reporting honestly rather than assumed."""
    feature_cols = get_feature_columns(train_df)
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    return importances.sort_values(ascending=False)


if __name__ == "__main__":
    from pathlib import Path
    features_path = Path(__file__).parent.parent / "data" / "processed" / "features.parquet"
    df = pd.read_parquet(features_path)

    split_idx = int(len(df) * 0.8)
    train_df, test_df = df.iloc[:split_idx], df.iloc[split_idx:]

    model = train_xgboost(train_df)
    preds = forecast_xgboost(model, test_df)
    mae = mean_absolute_error(test_df[TARGET_COL], preds)
    print(f"XGBoost MAE on holdout: {mae:.1f} MW")

    print("\nTop 10 feature importances:")
    print(feature_importance(model, train_df).head(10))
