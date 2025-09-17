import argparse, yaml
from pathlib import Path
from metrics_source import load_csv
from detectors import rolling_zscore_anomalies, isolation_forest_anomalies
from summarizer import templated_summary
from notifiers import print_notify


def load_config(path: str) -> dict:
    """Load YAML configuration file into a Python dictionary."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def suggest_action(row, history=None):
    """
    Generate a context-aware remediation suggestion for anomalies.

    Logic considers:
      - Correlations between CPU, Memory, and Latency
      - Severity levels (critical, warning, informational)
      - Duration / recurrence (if history of node anomalies is provided)

    Returns a multi-line string resembling a DevOps runbook recommendation.
    """

    # Extract metric values
    cpu = float(row.get("cpu", 0))
    mem = float(row.get("memory", 0))
    lat = float(row.get("latency_ms", 0))
    node = row.get("node", "unknown")

    # Default fallback action
    action = "⚠️ Anomaly detected. Investigate system health."

    # --- Correlation-based logic ---
    if cpu >= 90 and mem >= 85:
        # Both CPU + Memory critical → strong sign of saturation or leak
        action = (
            f"🚨 Critical: Node {node} shows CPU {cpu:.1f}% + Memory {mem:.1f}%.\n"
            "Likely cause: memory leak or workload saturation.\n"
            "Suggested Action: Restart affected pod and check garbage collection logs."
        )
    elif cpu >= 85 and lat >= 200:
        # High CPU combined with high latency → DB or downstream bottleneck
        action = (
            f"🚨 Critical: High CPU {cpu:.1f}% with Latency {lat:.0f}ms on {node}.\n"
            "Possible DB or downstream service bottleneck.\n"
            "Suggested Action: Profile DB queries and scale replicas if needed."
        )
    elif lat >= 250 and cpu < 70 and mem < 70:
        # Latency issue while resource usage normal → network issue
        action = (
            f"⚠️ Warning: Latency {lat:.0f}ms on {node} while CPU/Memory normal.\n"
            "Likely cause: network congestion or downstream dependency issue.\n"
            "Suggested Action: Check API gateway logs and network connectivity."
        )
    elif cpu >= 95:
        # Extreme CPU spike
        action = (
            f"🚨 Critical: CPU spike {cpu:.1f}% on {node}.\n"
            "Suggested Action: Kill runaway process or scale api-service replicas."
        )
    elif cpu >= 80:
        # Sustained CPU load but not maxed out
        action = (
            f"⚠️ Warning: Sustained CPU load {cpu:.1f}% on {node}.\n"
            "Suggested Action: Inspect logs for infinite loops or long-running jobs."
        )
    elif mem >= 90:
        # Memory close to OOM
        action = (
            f"🚨 Critical: Memory exhaustion {mem:.1f}% on {node}.\n"
            "Suggested Action: Restart pod, check heap dump, and tune JVM/GC params."
        )
    elif mem >= 75:
        # Elevated memory usage
        action = (
            f"⚠️ Warning: Elevated memory usage {mem:.1f}% on {node}.\n"
            "Suggested Action: Monitor caches and investigate object retention."
        )
    elif lat >= 150:
        # Latency moderately high
        action = (
            f"⚠️ Warning: Latency above 150ms ({lat:.0f}ms) on {node}.\n"
            "Suggested Action: Check DB indexes and downstream service health."
        )
    else:
        # Mild anomaly → no urgent remediation
        action = (
            f"ℹ️ Informational: Mild anomaly on {node}.\n"
            "Suggested Action: Monitor trends; no immediate remediation required."
        )

    # --- Historical duration check ---
    if history is not None:
        node_history = history[history["node"] == node]
        # If the same node has frequent anomalies → mark for deeper review
        if not node_history.empty and len(node_history) > 3:
            action += "\nNote: Multiple anomalies detected on this node recently → consider cordoning or replacing node."

    return action


def main(config_path: str):
    """
    Main entrypoint for the anomaly detection agent.

    Workflow:
      1. Load configuration
      2. Load metrics (CSV for demo, Prometheus in future)
      3. Apply anomaly detection (Z-score or Isolation Forest)
      4. Generate incident reports (templated + remediation suggestions)
      5. Output results to console and save artifacts for dashboard
    """

    # --- Load config ---
    cfg = load_config(config_path)
    src = cfg.get("source", {})
    det = cfg.get("detection", {})
    notif = cfg.get("notifier", {})
    runtime = cfg.get("runtime", {})

    # --- Load data ---
    if src.get("kind") == "csv":
        df = load_csv(src.get("path"))
    else:
        raise NotImplementedError("Only 'csv' source supported in this demo.")

    # --- Detect anomalies ---
    method = det.get("method", "rolling_zscore")
    if method == "rolling_zscore":
        out = rolling_zscore_anomalies(
            df, col="cpu",
            window=det.get("rolling_window", 20),
            zthr=det.get("zscore_threshold", 3.0)
        )
        anomalies = out[out["is_anomaly"]].copy()
        anomalies["metric"] = "cpu"
    else:
        out = isolation_forest_anomalies(
            df, cols=["cpu", "memory", "latency_ms"], contamination=0.02
        )
        anomalies = out[out["is_anomaly"]].copy()
        anomalies["metric"] = "composite"

    # --- Summarize and notify ---
    limit = runtime.get("limit_alerts", 10)
    reports = []
    for _, row in anomalies.tail(limit).iterrows():
        event = {
            "timestamp": row["timestamp"],
            "node": row.get("node", "unknown"),
            "metric": row.get("metric", "cpu"),
            "value": round(float(row.get("cpu", 0.0)), 2),
            "threshold": det.get("zscore_threshold", "N/A"),
            "suggestion": suggest_action(row),
        }
        msg = templated_summary(event)
        reports.append(msg)

        # Print to console if enabled
        if notif.get("print", True):
            print_notify(msg)

    # --- Save artifacts for dashboard ---
    out_dir = Path(__file__).resolve().parents[1] / "data"
    anomalies.tail(limit).to_csv(out_dir / "last_anomalies.csv", index=False)
    (out_dir / "last_reports.txt").write_text("\n\n".join(reports))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    main(args.config)
