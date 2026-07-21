import dash
from dash import Dash, html, dcc, Input, Output, State, ctx
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone


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
query_api  = client.query_api()


# =====================================
# LECTURA INICIAL DESDE INFLUXDB
# =====================================

def leer_estados_desde_influx():
    """
    Consulta el último valor de cada campo en InfluxDB.
    Si un campo no existe todavía, queda en 0 por defecto.
    """
    estados_leidos = {
        "islaP":  0,
        "piso1P": 0,
        "piso2P": 0,
        "piso3P": 0,
    }

    query = '''
    from(bucket: "microgrid")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "prueba")
        |> filter(fn: (r) =>
            r._field == "islaP"  or
            r._field == "piso1P" or
            r._field == "piso2P" or
            r._field == "piso3P")
        |> group(columns: ["_field"])
        |> last()
    '''

    try:
        tablas = query_api.query(query=query)
        for tabla in tablas:
            for record in tabla.records:
                campo = record.get_field()
                valor = int(record.get_value())
                if campo in estados_leidos:
                    estados_leidos[campo] = valor
                    print(f"[InfluxDB] Estado leído → {campo} = {valor}")
    except Exception as e:
        print(f"[InfluxDB] No se pudo leer el estado inicial: {e}")

    return estados_leidos


# =====================================
# VARIABLES DE ESTADO (cargadas desde InfluxDB)
# =====================================

print("Leyendo últimos estados desde InfluxDB...")
estados = leer_estados_desde_influx()
print(f"Estados iniciales: {estados}")


# =====================================
# ESTILOS
# =====================================

ESTILO_BOTON_APAGADO = {
    "width": "160px",
    "height": "60px",
    "fontSize": "16px",
    "fontWeight": "bold",
    "borderRadius": "8px",
    "border": "2px solid #555",
    "backgroundColor": "#cccccc",
    "color": "#333333",
    "cursor": "pointer",
    "margin": "10px",
}

ESTILO_BOTON_ENCENDIDO = {
    **ESTILO_BOTON_APAGADO,
    "backgroundColor": "#2ecc71",
    "color": "#ffffff",
    "border": "2px solid #27ae60",
}

ESTILO_ETIQUETA = {
    "fontSize": "14px",
    "color": "#555",
    "marginTop": "4px",
}

ESTILO_TARJETA = {
    "display": "inline-block",
    "textAlign": "center",
    "margin": "20px",
    "verticalAlign": "top",
}


# =====================================
# FUNCIÓN AUXILIAR
# =====================================

def estilo_boton(estado):
    """Devuelve el estilo según el estado (0 o 1)."""
    return ESTILO_BOTON_ENCENDIDO if estado == 1 else ESTILO_BOTON_APAGADO


def texto_boton(nombre, estado):
    nombres_visual = {
        "islaP":  "Isla",
        "piso1P": "Piso 1",
        "piso2P": "Piso 2",
        "piso3P": "Piso 3",
    }
    icono = "🟢" if estado == 1 else "⚫"
    etiqueta = nombres_visual.get(nombre, nombre)  # si no encuentra, usa el nombre original
    return f"{icono}  {etiqueta}"


def enviar_a_influx(campo, valor):
    """Escribe un campo en InfluxDB bajo la medición 'prueba'."""
    punto = (
        Point("prueba")
        .field(campo, float(valor))
        .time(datetime.now(timezone.utc), WritePrecision.NS)
    )
    write_api.write(bucket=bucket, org=org, record=punto)
    print(f"[InfluxDB] {campo} = {valor} → enviado correctamente.")


# =====================================
# APLICACIÓN DASH
# =====================================

print("Aplicación HMI iniciando...")

app = Dash(__name__)
server = app.server

def serve_layout():
    """
    Se ejecuta CADA VEZ que se carga o recarga la página en el navegador
    (a diferencia de un html.Div fijo, que solo se construye una vez al
    iniciar el servidor). Así el layout siempre refleja el último estado
    guardado en InfluxDB.
    """
    global estados
    estados = leer_estados_desde_influx()
    print(f"[Layout] Estados releídos al cargar la página: {estados}")

    return html.Div(
        style={
            "fontFamily": "Arial, sans-serif",
            "maxWidth": "700px",
            "margin": "40px auto",
            "padding": "20px",
            "backgroundColor": "#f9f9f9",
            "borderRadius": "12px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
        },
        children=[

            html.H1("Control Microrred", style={"textAlign": "center", "color": "#2c3e50"}),
            html.P(
                "Presiona un botón para cambiar su estado.",
                style={"textAlign": "center", "color": "#777", "marginBottom": "30px"}
            ),

            # ── Fila de botones ──
            html.Div(
                style={"textAlign": "center"},
                children=[

                    # islaP
                    html.Div(style=ESTILO_TARJETA, children=[
                        html.Button(
                            id="btn-islaP",
                            children=texto_boton("islaP", estados["islaP"]),
                            n_clicks=0,
                            style=estilo_boton(estados["islaP"])
                        ),
                        html.P(id="lbl-islaP", children=f"Estado: {estados['islaP']}", style=ESTILO_ETIQUETA),
                    ]),

                    # piso1P
                    html.Div(style=ESTILO_TARJETA, children=[
                        html.Button(
                            id="btn-piso1P",
                            children=texto_boton("piso1P", estados["piso1P"]),
                            n_clicks=0,
                            style=estilo_boton(estados["piso1P"])
                        ),
                        html.P(id="lbl-piso1P", children=f"Estado: {estados['piso1P']}", style=ESTILO_ETIQUETA),
                    ]),

                    # piso2P
                    html.Div(style=ESTILO_TARJETA, children=[
                        html.Button(
                            id="btn-piso2P",
                            children=texto_boton("piso2P", estados["piso2P"]),
                            n_clicks=0,
                            style=estilo_boton(estados["piso2P"])
                        ),
                        html.P(id="lbl-piso2P", children=f"Estado: {estados['piso2P']}", style=ESTILO_ETIQUETA),
                    ]),

                    # piso3P
                    html.Div(style=ESTILO_TARJETA, children=[
                        html.Button(
                            id="btn-piso3P",
                            children=texto_boton("piso3P", estados["piso3P"]),
                            n_clicks=0,
                            style=estilo_boton(estados["piso3P"])
                        ),
                        html.P(id="lbl-piso3P", children=f"Estado: {estados['piso3P']}", style=ESTILO_ETIQUETA),
                    ]),

                ]
            ),

            # ── Log de último evento ──
            html.Hr(style={"marginTop": "30px"}),
            html.P(
                id="log",
                children="Sin cambios aún.",
                style={"textAlign": "center", "color": "#999", "fontStyle": "italic"}
            ),

            # ── Timer: dispara una relectura periódica de InfluxDB ──
            dcc.Interval(
                id="intervalo-actualizacion",
                interval=3000,  # cada 3000 ms = 3 segundos
                n_intervals=0
            ),
        ]
    )


# IMPORTANTE: se asigna la FUNCIÓN (sin llamarla con "()"),
# para que Dash la ejecute en cada request/recarga.
app.layout = serve_layout


# =====================================
# CALLBACK ÚNICO (todos los botones)
# =====================================

@app.callback(
    # Salidas: texto + estilo de cada botón, etiqueta de estado, log
    Output("btn-islaP",  "children"),
    Output("btn-islaP",  "style"),
    Output("lbl-islaP",  "children"),

    Output("btn-piso1P", "children"),
    Output("btn-piso1P", "style"),
    Output("lbl-piso1P", "children"),

    Output("btn-piso2P", "children"),
    Output("btn-piso2P", "style"),
    Output("lbl-piso2P", "children"),

    Output("btn-piso3P", "children"),
    Output("btn-piso3P", "style"),
    Output("lbl-piso3P", "children"),

    Output("log", "children"),

    # Entradas: clicks de cada botón + tick del timer
    Input("btn-islaP",  "n_clicks"),
    Input("btn-piso1P", "n_clicks"),
    Input("btn-piso2P", "n_clicks"),
    Input("btn-piso3P", "n_clicks"),
    Input("intervalo-actualizacion", "n_intervals"),

    prevent_initial_call=True
)
def manejar_botones(n_islaP, n_piso1P, n_piso2P, n_piso3P, n_intervalos):
    """
    Se dispara por dos tipos de eventos:
      1) Clic en un botón  -> invierte el estado y lo ESCRIBE en InfluxDB.
      2) Tick del dcc.Interval -> solo LEE InfluxDB y refresca la vista,
         para que los cambios hechos por otros usuarios se vean sin recargar.
    """

    disparador = ctx.triggered_id  # "btn-islaP", "btn-piso1P", ... o "intervalo-actualizacion"

    if disparador == "intervalo-actualizacion":
        # Solo refrescar con lo último que haya en InfluxDB (sin escribir nada)
        estados_actuales = leer_estados_desde_influx()
        estados.update(estados_actuales)

        return (
            texto_boton("islaP",  estados["islaP"]),  estilo_boton(estados["islaP"]),  f"Estado: {estados['islaP']}",
            texto_boton("piso1P", estados["piso1P"]), estilo_boton(estados["piso1P"]), f"Estado: {estados['piso1P']}",
            texto_boton("piso2P", estados["piso2P"]), estilo_boton(estados["piso2P"]), f"Estado: {estados['piso2P']}",
            texto_boton("piso3P", estados["piso3P"]), estilo_boton(estados["piso3P"]), f"Estado: {estados['piso3P']}",
            dash.no_update,  # no tocar el log en un refresco automático
        )

    # --- A partir de aquí: fue un clic de botón ---
    campo = disparador.replace("btn-", "")  # e.g. "islaP"

    # Invertir estado
    estados_actuales = leer_estados_desde_influx()
    estados[campo] = 1 - estados_actuales[campo]
    nuevo_valor = estados[campo]

    # Guardar en InfluxDB
    enviar_a_influx(campo, nuevo_valor)

    # Construir mensaje de log
    accion = "ACTIVADO 🟢" if nuevo_valor == 1 else "DESACTIVADO ⚫"
    mensaje_log = f"[{datetime.now().strftime('%H:%M:%S')}]  {campo} → {accion}  (valor: {nuevo_valor})"

    # Devolver los 13 outputs en orden
    return (
        texto_boton("islaP",  estados["islaP"]),  estilo_boton(estados["islaP"]),  f"Estado: {estados['islaP']}",
        texto_boton("piso1P", estados["piso1P"]), estilo_boton(estados["piso1P"]), f"Estado: {estados['piso1P']}",
        texto_boton("piso2P", estados["piso2P"]), estilo_boton(estados["piso2P"]), f"Estado: {estados['piso2P']}",
        texto_boton("piso3P", estados["piso3P"]), estilo_boton(estados["piso3P"]), f"Estado: {estados['piso3P']}",
        mensaje_log,
    )


# =====================================
# EJECUTAR
# =====================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=True
    )