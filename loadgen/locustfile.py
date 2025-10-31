from locust import User, task, between
from paho.mqtt import client as mqtt
import ssl, time, os, random


BROKER=os.getenv("BROKER","localhost")
PORT=int(os.getenv("PORT","8883"))
CA=os.getenv("CA","infra/mosquitto/certs/ca/ca.crt")


class MqttUser(User):
wait_time = between(0.5, 2.0)


def on_start(self):
cn = f"sensor_{random.randint(1000,9999)}"
self.client = mqtt.Client(client_id=cn, protocol=mqtt.MQTTv5)
self.client.tls_set(ca_certs=CA, tls_version=ssl.PROTOCOL_TLSv1_3)
self.client.connect(BROKER, PORT, 60)
self.client.loop_start()
self.topic=f"sensors/stackA/{cn}"


@task
def publish(self):
payload=b"{}"
self.client.publish(self.topic, payload, qos=1)


def on_stop(self):
self.client.loop_stop()
self.client.disconnect()