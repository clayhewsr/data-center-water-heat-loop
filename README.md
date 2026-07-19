# Data Center Water & Heat Loop Ecosystem

This project presents a closed-loop ecosystem for water reuse in data-center cooling, waste-heat recovery, and simulated operations monitoring to support resilient and sustainable infrastructure planning.

![Data Center Water & Heat Loop Ecosystem](assets/data%20center%20eco.png)

## Working Prototype

The Streamlit operations dashboard currently runs on simulated data and monitors:

- water flow
- supply and return temperatures
- tank level
- pump pressure
- compute load
- recovered heat
- thermal storage
- system health

## Run Locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Core Architecture

- Closed-Loop Water System
- Liquid Cooling
- Heat Recovery
- Sensor and Monitoring Layer
- Operations Dashboard

## Repository Guide

- [dashboard.py](dashboard.py)
- [docs/](docs/)
- [diagrams/](diagrams/)
- [demo/](demo/)
- [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)
- [ROADMAP.md](ROADMAP.md)

## Current Status

- Version: v0.2.0 prototype
- Dashboard: working simulation
- Real sensor integration: future work
- Cloud deployment: future work

## Disclaimer

This repository is a public engineering concept and simulated prototype. It is not a construction specification or a live facility control system.
