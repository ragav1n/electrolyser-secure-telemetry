#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
CN=${1:?Usage: $0 <client_common_name>}
OUT=../infra/mosquitto/certs/clients/${CN}
mkdir -p "$OUT"


openssl req -new -newkey rsa:4096 -nodes \
-keyout "$OUT/${CN}.key" \
-out "$OUT/${CN}.csr" \
-subj "/CN=${CN}"


openssl x509 -req -in "$OUT/${CN}.csr" \
-CA ca/certs/ca.crt -CAkey ca/private/ca.key -CAcreateserial \
-out "$OUT/${CN}.crt" -days 365 -sha256 \
-extfile <(printf "extendedKeyUsage=clientAuth\n")


rm -f "$OUT/${CN}.csr"