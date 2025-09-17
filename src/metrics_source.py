import pandas as pd

def load_csv(path: str) -> pd.DataFrame:
    """
    Load a CSV file containing time-series metrics.

    Parameters
    ----------
    path : str
        File path to the CSV (expected to have a 'timestamp' column).

    Returns
    -------
    df : pd.DataFrame
        Pandas DataFrame sorted by timestamp, with 'timestamp' parsed as datetime.
    """
    # Read CSV into DataFrame, automatically parsing the "timestamp" column as datetime
    df = pd.read_csv(path, parse_dates=["timestamp"])

    # Ensure rows are sorted chronologically for time-series analysis
    return df.sort_values("timestamp")
