from dash import Dash, html, Input, Output
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone
import random


# =====================================
# CONFIGURACIÓN INFLUXDB
# =====================================

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


# =====================================
# PÁGINA WEB
# =====================================

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1("Microrred"),

    html.H2(
        id="valor",
        children="Valor: --"
    ),

    html.Button(
        "Actualizar valor",
        id="boton",
        n_clicks=0
    )

])


# =====================================
# BOTÓN
# =====================================

@app.callback(
    Output("valor", "children"),
    Input("boton", "n_clicks"),
    prevent_initial_call=True
)
def actualizar_valor(n_clicks):

    # Generar número aleatorio
    numero = random.randint(1, 100)

    print("Nuevo valor:", numero)

    # Crear punto para InfluxDB
    punto = (
        Point("prueba")
        .field("valor", float(numero))
        .time(datetime.now(timezone.utc), WritePrecision.NS)
    )

    # Guardar en InfluxDB
    write_api.write(
        bucket=bucket,
        org=org,
        record=punto
    )

    print("Dato enviado correctamente.")

    # Actualizar página
    return f"Valor: {numero}"


# =====================================
# EJECUTAR
# =====================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=True
    )