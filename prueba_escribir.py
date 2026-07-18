from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime


# =========================
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# =====================================
# CONFIGURACIÃN
# =====================================
# ===== CONFIGURACIÃN =====
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
token = "ogJtAMxVe9SO75JNiIEdLhoy7UKM0DyH7ZD-O5Q-Xyg3xjY8jY2L_Cpm6hvreBsomzvOz3FPX9qg09PD3QQQmg=="
org = "colombia"
bucket = "microgrid"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

punto = (
    Point("prueba")
    .field("valor", 1586.45)
    .time(datetime.utcnow(), WritePrecision.NS)
)

write_api.write(bucket=bucket, org=org, record=punto)

print("Dato enviado correctamente.")

client.close()