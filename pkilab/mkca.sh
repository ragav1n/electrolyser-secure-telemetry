#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ca/{certs,crl,newcerts,private}
: > ca/index.txt
echo 1000 > ca/serial


openssl req -x509 -new -nodes \
-config openssl.cnf \
-keyout ca/private/ca.key \
-out ca/certs/ca.crt \
-subj "/CN=Electrolyser Local Root CA" \
-days 3650 -sha256


echo "CA created at pkilab/ca"