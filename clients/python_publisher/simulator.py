import ssl, time, argparse, sys
from pathlib import Path
import yaml
from paho.mqtt import client as mqtt
from utils.payloads import synthetic_payload
from utils.crypto import maybe_encrypt

def load_cfg(path: Path) -> dict:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()

    CFG = load_cfg(Path(args.config))
    M, P = CFG["mqtt"], CFG["payload_encryption"]
    # add at the start of main() in simulator.py, then run once
    print("CFG topic:", M["topic"], "client CN:", M["client_id"])

    # ✅ Use Callback API v2 (fixes deprecation warning)
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=M["client_id"],
        protocol=mqtt.MQTTv5,
    )

    # ✅ Build an SSLContext without hardcoding TLSv1_3 (works on LibreSSL too)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Try to require TLS 1.3 if available, else fall back gracefully
    if hasattr(ssl, "TLSVersion"):
        # Prefer TLS 1.3 if your Python/OpenSSL supports it
        try:
            ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        except Exception:
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    # Load CA and client certs
    ctx.load_verify_locations(M["ca"])
    ctx.load_cert_chain(certfile=M["cert"], keyfile=M["key"])
    ctx.check_hostname = False  # broker CN is not a real DNS name locally

    client.tls_set_context(ctx)
    client.tls_insecure_set(False)

    def on_connect(client, userdata, flags, reason_code, properties):
        print("Connected:", reason_code)

    def on_disconnect(client, userdata, reason_code, properties):
        print("Disconnected:", reason_code)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(M["host"], int(M["port"]), keepalive=60)
    client.loop_start()
    try:
        while True:
            payload = synthetic_payload(M["client_id"])
            payload = maybe_encrypt(payload, P["key_hex"] if P.get("enabled") else None)
            info = client.publish(M["topic"], payload, qos=int(M["qos"]), retain=False)
            info.wait_for_publish()
            print("Published message ID:", info.mid)
            time.sleep(float(CFG["telemetry"]["interval_secs"]))
    except KeyboardInterrupt:
        print("\nExiting publisher...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
