#!/usr/bin/env bash
set -euo pipefail
# 1) Create CA and broker cert
( cd pkilab && ./mkca.sh )
( cd pkilab && ./issue_broker_cert.sh mosquitto )
# 2) Issue one test client cert
( cd pkilab && ./issue_client_cert.sh sensor_001 )
# 3) Start the stack
docker compose up -d --build
# 4) Print endpoints
echo "MQTTS: mqtts://localhost:8883"
echo "InfluxDB UI: http://localhost:8086"
echo "Grafana UI: http://localhost:3000 (admin creds from .env)"