from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime



# =====================================
# CONFIGURACIÓN
# =====================================
# ===== CONFIGURACIÓN =====
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
token = "ogJtAMxVe9SO75JNiIEdLhoy7UKM0DyH7ZD-O5Q-Xyg3xjY8jY2L_Cpm6hvreBsomzvOz3FPX9qg09PD3QQQmg=="
org = "colombia"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()

query = '''
from(bucket: "microgrid")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "prueba")
  |> last()
'''

tables = query_api.query(query=query)

for table in tables:
    for record in table.records:
        print(
            f"Hora: {record.get_time()} | "
            f"Campo: {record.get_field()} | "
            f"Valor: {record.get_value()}"
        )

client.close()