import ssl, socket


def test_tls_13_enabled():
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.minimum_version = ssl.TLSVersion.TLSv1_3
ctx.load_verify_locations("infra/mosquitto/certs/ca/ca.crt")
with socket.create_connection(("localhost", 8883), timeout=3) as sock:
with ctx.wrap_socket(sock, server_hostname="mosquitto") as ssock:
assert ssock.version() == 'TLSv1.3'