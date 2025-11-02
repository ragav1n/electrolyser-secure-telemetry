# Electrolyser Secure Telemetry System

### End-to-End Encrypted, Scalable, and Fault-Resilient IoT Telemetry Stack for Hydrogen Electrolyser Farms

This repository contains a **complete, open-source prototype** of a secure, high-performance telemetry pipeline for hydrogen electrolyser farms.
It demonstrates **end-to-end encryption**, **mutual TLS authentication**, **secure MQTT transport**, and **real-time visualization** of sensor data across 100–1000 devices.

---

## System Overview

**Goal:** Enable secure, scalable collection and monitoring of sensor telemetry (temperature, pressure, hydrogen flow, purity, voltage, current) from distributed electrolysers.

---

### Architecture Diagram

![IoT Sensor System Architecture (Horizontal)](https://github.com/user-attachments/assets/36d12248-ed12-4703-bb24-dfc24ca29e1e)

-----

## Core Features

| Feature | Description |
|:--------------------------|:--------------------------------------------------------------------------------------|
| **End-to-End Encryption** | TLS 1.3 with mutual authentication using X.509 certificates |
| **Scalable Simulation** | 100–1000 concurrent MQTT clients using Python/Paho |
| **QoS 1 Reliability** | Guaranteed delivery for each published message |
| **Self-Signed PKI** | Custom CA issuing per-sensor, broker, and bridge certificates |
| **Secure Broker** | Dockerized Eclipse Mosquitto with ACL and cert-based access control |
| **Telemetry Storage** | **InfluxDB v2** with per-bucket authentication and retention policies |
| **Visualization** | **Grafana** dashboards (Temperature, Pressure, Flow, Purity, Voltage, Current) |
| **Optional AES Layer** | Payload-level **AES-256** encryption for data-at-rest protection |
| **Automated Ingestion** | Telegraf `mqtt_consumer` → InfluxDB pipeline |
| **Load Testing** | **Locust** + Pytest harness for 100–1000 client validation |
| **Fault Injection** | Simulated purity drops, voltage flickers, and network drops |
| **Benchmark Dashboard** | Real-time metrics on latency, CPU, handshake success, and packet loss |

-----

## Repository Structure

```
electrolyser-secure-telemetry/
├── clients/
│   ├── python_publisher/
│   │   ├── simulator.py           # single-sensor simulator
│   │   ├── launch_fleet.py        # spawns 100+ simulators
│   │   ├── utils/
│   │   │   ├── payloads.py        # synthetic data generator
│   │   │   └── crypto.py          # AES-256 payload encryption
│   │   └── config.yaml            # base MQTT + TLS config
│   └── esp32/                     # (optional) Paho-ESP client code
│
├── infra/
│   ├── mosquitto/
│   │   ├── mosquitto.conf
│   │   ├── aclfile
│   │   └── certs/
│   │       ├── ca/                # CA keypair
│   │       ├── broker/            # broker cert
│   │       ├── clients/           # per-sensor certs
│   │       └── telegraf_bridge/   # bridge cert
│   ├── telegraf/
│   │   └── telegraf.conf
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── influxdb.yaml
│           └── dashboards/
│               └── electrolyser.json
│
├── pkilab/
│   ├── mkca.sh                    # initialize CA
│   ├── issue_broker_cert.sh       # broker cert
│   ├── issue_telegraf_cert.sh     # bridge cert
│   ├── issue_many_clients.sh      # issue 100+ client certs
│
├── docker-compose.yml             # launches the entire stack
├── .env                           # Influx/Grafana creds
└── README.md
```

-----

## Setup Guide

### 1️. Prerequisites

  - **Docker** + **Docker Compose**
  - **Python** $\ge 3.10$
  - **OpenSSL**
  - (Optional) ESP32 with Paho MQTT client

### 2️. Configure Environment

Edit `.env` with your desired credentials and tokens:

```bash
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=admin123
INFLUXDB_ORG=electrolyser
INFLUXDB_BUCKET=telemetry
INFLUXDB_TOKEN=my-local-token
GRAFANA_USER=admin
GRAFANA_PASS=admin
```

### 3️. Initialize Certificates

The Public Key Infrastructure (PKI) scripts create all necessary X.509 certificates and keys for mutual TLS.

```bash
bash pkilab/mkca.sh                  # Create the Certificate Authority (CA)
bash pkilab/issue_broker_cert.sh mosquitto    # Create the broker's server certificate
bash pkilab/issue_telegraf_cert.sh telegraf_bridge # Create the Telegraf client certificate
bash pkilab/issue_many_clients.sh 100 # Create 100 client certificates
```

### 4️. Launch the Stack

Start all core infrastructure components: Mosquitto, InfluxDB, and Grafana.

```bash
docker compose up -d
```

**Access Points:**

  * **Mosquitto:** port `8883` (mTLS)
  * **InfluxDB UI:** `http://localhost:8086`
  * **Grafana:** `http://localhost:3000`

### 5️. Simulate a Sensor

Run a single, secure client to verify the basic data pipeline:

```
cd clients/python_publisher
python simulator.py --config ./config.yaml
```

### 6️. Scale to 100+ Sensors

Launch a fleet of concurrent, secure clients for load simulation:

```
python launch_fleet.py --count 150 --stack stackA
```

### 7️. View Real-Time Dashboard

Open Grafana → `http://localhost:3000` → Dashboards → **Electrolyser Telemetry**

-----

## Data Flow Example

A typical **MQTT JSON** payload published by a sensor:

```json
{
  "sensor_id": "sensor_001",
  "temperature_c": 42.3,
  "pressure_bar": 10.4,
  "h2_flow_sccm": 108.5,
  "purity_pct": 99.8,
  "voltage_v": 2.03,
  "current_a": 10.1
}
```

Telegraf transforms this into **InfluxDB Line Protocol**:

```
electrolyser,sensor_id=sensor_001 temperature_c=42.3,pressure_bar=10.4,h2_flow_sccm=108.5,...
```

Grafana panels query the data using **Flux**:

```flux
from(bucket: "telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "electrolyser" and r._field == "temperature_c")
  |> filter(fn: (r) => r.sensor_id =~ /${sensor:regex}/)
```

-----



