# Sensor Network Diagram

```mermaid
flowchart LR
    A[Temperature Sensors]
    B[Pressure Sensors]
    C[Flow Sensors]
    D[Water Quality Sensors]
    E[Leak Detection]
    F[Vibration Sensors]

    A --> G[Data Collection Layer]
    B --> G
    C --> G
    D --> G
    E --> G
    F --> G

    G --> H[AI Control Center]
    H --> I[Operations Dashboard]
    H --> J[Predictive Analytics]
    H --> K[Safety & Resiliency]
```

## Purpose

This diagram illustrates how distributed sensors continuously monitor the cooling system, water infrastructure, and equipment health while providing real-time operational awareness and predictive analytics.
