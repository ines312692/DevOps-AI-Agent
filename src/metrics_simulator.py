import pandas as pd
import numpy as np
import os

# Path to output CSV file (../data/sample_metrics.csv relative to this script)
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "sample_metrics.csv")

# Ensure the data directory exists (auto-create if missing)
os.makedirs(os.path.dirname(OUT), exist_ok=True)


def simulate_series(start, periods=600, freq_s=30, base=35, noise=5, spikes=5):
    """
    Generate a synthetic time series dataset for system metrics (CPU, memory, latency).

    Parameters
    ----------
    start : pd.Timestamp
        Start time for the series.
    periods : int, optional (default=600)
        Number of data points to generate.
    freq_s : int, optional (default=30)
        Sampling frequency in seconds.
    base : float, optional (default=35)
        Base CPU usage around which variation is added.
    noise : float, optional (default=5)
        Standard deviation of random noise applied to CPU values.
    spikes : int, optional (default=5)
        Number of random anomaly spikes to inject into CPU values.

    Returns
    -------
    df : pd.DataFrame
        Synthetic dataset with columns:
          - timestamp : datetime values
          - node      : simulated node IDs ("node-a", "node-b", "node-c")
          - cpu       : CPU usage percentage (0–100)
          - memory    : Memory usage percentage (0–100)
          - latency_ms: Request latency in milliseconds
    """
    # Create time axis (regular intervals from start time)
    times = [start + i * pd.Timedelta(seconds=freq_s) for i in range(periods)]

    # Base CPU load with random noise
    values = base + np.random.normal(0, noise, size=periods)

    # Add sinusoidal variation to simulate periodic load patterns
    x = np.linspace(0, 4 * np.pi, periods)
    values += 8 * np.sin(x)

    # Inject random anomaly spikes into CPU usage
    spike_idx = np.random.choice(periods, size=spikes, replace=False)
    for idx in spike_idx:
        values[idx] += np.random.uniform(35, 60)

    # Keep CPU values within [0, 100]
    values = np.clip(values, 0, 100)

    # Assemble DataFrame with CPU, memory, and latency metrics
    return pd.DataFrame({
        "timestamp": times,
        "node": np.random.choice(["node-a", "node-b", "node-c"], size=periods),
        "cpu": values,
        # Memory: base ~40%, add sinusoidal + Gaussian noise
        "memory": np.clip(40 + np.random.normal(0, 6, size=periods) + 6 * np.cos(x), 0, 100),
        # Latency: base ~80ms, add sinusoidal + Gaussian noise
        "latency_ms": np.clip(80 + 15 * np.sin(2 * x) + np.random.normal(0, 10, periods), 10, 400)
    })


if __name__ == "__main__":
    # Example run: generate ~900 points (~5 hours of data at 20s intervals)
    start = pd.Timestamp.utcnow().floor('s') - pd.Timedelta(minutes=300)
    df = simulate_series(start, periods=900, freq_s=20, base=35, noise=6, spikes=12)

    # Sort chronologically (important if spikes shuffled order)
    df.sort_values("timestamp", inplace=True)

    # Save dataset to CSV
    df.to_csv(OUT, index=False)
    print(f"Wrote demo metrics to {OUT}")
