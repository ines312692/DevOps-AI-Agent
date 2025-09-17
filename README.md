# DevOps AI Agent: Automated Anomaly Detection & Incident Summarization

This project demonstrates how to build an **AI-powered monitoring agent** for DevOps.  

It automatically:
1. **Collects metrics** (simulated or real)
2. **Detects anomalies** (threshold-based and ML-based)
3. **Summarizes incidents in plain English**
4. **Notifies engineers** (console + dashboard UI)
5. **Visualizes metrics and anomalies** in a Streamlit dashboard

It mimics how real monitoring platforms like **Datadog, Prometheus, and PagerDuty** work but with a built-in AI summarizer that generates **context-aware remediation suggestions**.

---

## Project Structure

```
devops-ai-agent/
│── README.md                # Project documentation
│── requirements.txt         # Python dependencies
│── configs/
│   └── config.yaml          # Agent configuration
│── data/
│   └── sample_metrics.csv   # Synthetic metrics dataset (generated)
│── src/
│   ├── metrics_simulator.py # Generate synthetic system metrics
│   ├── metrics_source.py    # Load metrics from CSV (or future Prometheus API)
│   ├── detectors.py         # Rolling Z-Score & Isolation Forest anomaly detection
│   ├── summarizer.py        # Converts anomalies into human-readable reports
│   ├── notifiers.py         # Sends reports to console (extensible to Slack/email)
│   └── agent.py             # Main monitoring agent logic
└── streamlit_app.py         # Interactive monitoring dashboard
```

---

## Installation

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/your-username/devops-ai-agent.git
cd devops-ai-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # On Mac/Linux
.venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Quickstart

### 1. Generate Demo Metrics
Create a dataset with **CPU, Memory, and Latency** values, including injected anomalies:

```bash
python src/metrics_simulator.py
```

This writes a CSV file to `data/sample_metrics.csv`.



### 2. Run the Agent
Detect anomalies and generate incident reports:

```bash
python src/agent.py --config configs/config.yaml
```

Output:
- **Console logs** with structured incident reports
- **data/last_anomalies.csv** — structured anomaly rows
- **data/last_reports.txt** — human-readable incident summaries

Example terminal output:

```
=== INCIDENT REPORT ===
🚨 Critical: Node node-b shows CPU 92.5% + Memory 87.1%.
Likely cause: memory leak or workload saturation.
Suggested Action: Restart affected pod and check garbage collection logs.
=======================
```

### 3. Launch the Dashboard
Visualize metrics and incidents in a **Streamlit dashboard**:

```bash
streamlit run streamlit_app.py
```

This opens a browser at [http://localhost:8501](http://localhost:8501).

You’ll see:
- **Metrics charts** (CPU, Memory, Latency over time)
- **Anomalies table** (last run anomalies)
- **Incident Reports** (color-coded by severity: red, yellow, blue)

---

## How It Works

### Step 1. Metrics Source
- Synthetic dataset (`metrics_simulator.py`) simulates load patterns, spikes, and anomalies.
- Future extension: pull real metrics from **Prometheus API**.

### Step 2. Anomaly Detection (`detectors.py`)
- **Rolling Z-Score**: flags deviations from moving average (good for spikes).
- **Isolation Forest (ML)**: unsupervised anomaly detection across multiple metrics.

### Step 3. Summarization (`summarizer.py`)
- Converts anomalies into **plain English reports**.
- Includes **context-aware remediation suggestions**:
    - CPU + Memory high → memory leak suspicion.
    - CPU high + Latency high → DB bottleneck.
    - Latency high only → network issue.

### Step 4. Notifications (`notifiers.py`)
- Current: Console (`print_notify`)
- Extensible to Slack, Email, PagerDuty.

### Step 5. Visualization (`streamlit_app.py`)
- Displays metrics & incidents in **real time**.
- Color-coded severity → easy triage.
- Auto-refresh every 10 seconds.

---

## Example Dashboard

**Incident Reports Example:**

```
🚨 Critical: Node node-b shows CPU 92.5% + Memory 87.1%.
Likely cause: memory leak or workload saturation.
Suggested Action: Restart affected pod and check garbage collection logs.

⚠️ Warning: Latency 210ms on node-c while CPU/Memory normal.
Likely cause: network congestion or downstream dependency issue.
Suggested Action: Check API gateway logs and network connectivity.
```

**Dashboard View:**
- CPU/Memory/Latency chart
- Anomalies table
- Incident reports (red/yellow/blue alerts)

---

## Configuration

Edit **`configs/config.yaml`**:

```yaml
source:
  kind: csv
  path: data/sample_metrics.csv

detection:
  method: rolling_zscore        # Options: rolling_zscore | isolation_forest
  zscore_threshold: 3.0
  rolling_window: 20

notifier:
  print: true                   # Console output

runtime:
  limit_alerts: 10              # Max anomalies to report per run
```

---

## Key Features
- **AI-style incident summaries** (not just anomaly flags).
- **Context-aware remediation suggestions** (playbook-like).
- **Color-coded severity reports**.
- **Interactive Streamlit dashboard**.
- Extensible: swap CSV with **Prometheus**, add Slack/email alerts.

---

## Future Improvements
- Continuous monitoring agent (loop instead of one-shot run).
- Integration with **Prometheus/Grafana APIs**.
- Replace templated summarizer with **LLM-powered reasoning**.
- Extend notifiers: Slack, PagerDuty, email alerts.
- Historical trend analysis & anomaly correlation.

---

## Why This Project Matters
- Shows ability to design **real-world monitoring systems**.
- Demonstrates **data engineering, ML anomaly detection, and DevOps awareness**.
- Recruiters & managers see:
    - You can **detect problems automatically**.
    - You can **summarize incidents like an AI SRE assistant**.
    - You understand **operational workflows** beyond just coding.

---

## Tech Stack
- **Python** — Data processing & orchestration
- **Pandas / NumPy** — Time-series manipulation
- **Scikit-learn** — Isolation Forest anomaly detection
- **Streamlit** — Interactive dashboard
- **YAML** — Configurable agent

![Demo](assets/demo.gif)
