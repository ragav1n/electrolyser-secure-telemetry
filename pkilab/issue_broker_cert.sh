#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
BROKER_CN=${1:-mosquitto}
OUT=../infra/mosquitto/certs
mkdir -p "$OUT/broker" "$OUT/ca"

# Broker key & CSR
openssl req -new -newkey rsa:4096 -nodes \
  -keyout "$OUT/broker/broker.key" \
  -out "$OUT/broker/broker.csr" \
  -subj "/CN=${BROKER_CN}"

# Sign CSR
openssl x509 -req -in "$OUT/broker/broker.csr" \
  -CA ca/certs/ca.crt -CAkey ca/private/ca.key -CAcreateserial \
  -out "$OUT/broker/broker.crt" -days 825 -sha256 \
  -extfile <(printf "subjectAltName=DNS:%s,IP:127.0.0.1\nextendedKeyUsage=serverAuth\n" "$BROKER_CN")

rm -f "$OUT/broker/broker.csr"

# ✅ Correct destination for CA file
cp ca/certs/ca.crt "$OUT/ca/ca.crt"
echo "Broker certs ready at $OUT/broker ; CA at $OUT/ca/ca.crt"