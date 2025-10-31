import json, random, time


def synthetic_payload(sensor_id: str):
# Simple, reproducible-ish telemetry with small noise
    base = {
        "sensor_id": sensor_id,
        "ts": int(time.time() * 1000),
        "temperature_c": round(random.uniform(25.0, 60.0), 2),
        "pressure_bar": round(random.uniform(1.0, 10.0), 3),
        "h2_flow_sccm": round(random.uniform(50.0, 500.0), 1),
        "purity_pct": round(random.uniform(98.0, 99.999), 3),
        "voltage_v": round(random.uniform(1.6, 2.2), 3),
        "current_a": round(random.uniform(50.0, 300.0), 2),
    }

    return json.dumps(base).encode()