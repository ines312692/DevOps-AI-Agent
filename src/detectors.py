import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def rolling_zscore_anomalies(df: pd.DataFrame, col: str, window: int = 20, zthr: float = 3.0):
    """
    Detect anomalies in a time-series column using rolling Z-score.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing time-series metrics.
    col : str
        Column name (e.g., "cpu") on which to compute anomalies.
    window : int, optional (default=20)
        Rolling window size for computing mean and std deviation.
    zthr : float, optional (default=3.0)
        Z-score threshold beyond which values are flagged as anomalies.

    Returns
    -------
    df : pd.DataFrame
        Copy of input DataFrame with two additional columns:
          - "zscore": computed rolling z-score
          - "is_anomaly": True if absolute z-score >= threshold
    """
    # Extract column values as floats
    s = df[col].astype(float)

    # Compute rolling mean and std dev
    mu = s.rolling(window, min_periods=window).mean()
    sd = s.rolling(window, min_periods=window).std(ddof=0)

    # Z-score = (value - mean) / std
    z = (s - mu) / (sd.replace(0, np.nan))

    # Copy DataFrame to avoid side effects
    df = df.copy()
    df["zscore"] = z
    df["is_anomaly"] = (df["zscore"].abs() >= zthr)

    return df


def isolation_forest_anomalies(df: pd.DataFrame, cols, contamination=0.02, random_state=42):
    """
    Detect anomalies in multiple metrics using Isolation Forest.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing metrics (e.g., ["cpu", "memory", "latency_ms"]).
    cols : list
        List of column names to use as features for anomaly detection.
    contamination : float, optional (default=0.02)
        Proportion of expected anomalies in the dataset.
    random_state : int, optional (default=42)
        Seed for reproducibility.

    Returns
    -------
    df : pd.DataFrame
        Copy of input DataFrame with an additional column:
          - "is_anomaly": True if flagged as anomaly by Isolation Forest
    """
    # Extract feature matrix with NaN handling
    X = df[cols].astype(float).fillna(method="ffill").fillna(method="bfill")

    # Train Isolation Forest
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state
    )
    model.fit(X)

    # Predictions: -1 = anomaly, 1 = normal
    pred = model.predict(X)

    df = df.copy()
    df["is_anomaly"] = (pred == -1)

    return df
