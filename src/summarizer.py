import textwrap
from typing import Dict

def templated_summary(event: Dict) -> str:
    """
    Generate a human-readable incident summary from an anomaly event.

    Parameters
    ----------
    event : dict
        Dictionary containing anomaly details. Expected keys:
          - "timestamp": datetime or string
          - "metric": metric type (e.g., "cpu", "memory", "latency_ms")
          - "node": affected node/service identifier
          - "value": numeric value of the metric
          - "threshold": threshold or rule that triggered the anomaly
          - "suggestion": recommended remediation action (string)

    Returns
    -------
    str
        A formatted, multi-line string summarizing the incident in a
        human-readable way, ready to be printed to console or displayed in UI.
    """
    # Extract fields safely from event dictionary
    ts = event.get("timestamp")

    # Ensure timestamp is stringified (if datetime, use isoformat)
    when = ts if isinstance(ts, str) else getattr(ts, "isoformat", lambda: str(ts))()

    # Other fields with sensible defaults
    metric = event.get("metric", "cpu")
    node = event.get("node", "unknown")
    value = event.get("value", "N/A")
    threshold = event.get("threshold", "N/A")
    suggestion = event.get("suggestion", "Investigate logs or scale pods.")

    # Build a structured, user-friendly incident report
    return textwrap.dedent(f"""
    {suggestion}
    • Time: {when}
    • Node: {node}
    • Metric: {metric}
    • Value: {value}
    """).strip()
