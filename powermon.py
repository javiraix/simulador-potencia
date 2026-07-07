import streamlit as st

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(page_title="Simulador de Consumo Eléctrico", page_icon="⚡", layout="centered")

LIMITE_CONTRATADO = 3300  # Vatios

st.title("⚡ Panel de Control y Coincidencia de Potencias")
st.write(f"Simulador en tiempo real para control del ICP (Límite: **{LIMITE_CONTRATADO:,} W**)".replace(",", "."))
st.markdown("---")

# ============================================================
# BASE DE DATOS DE ELECTRODOMÉSTICOS
# Potencia nominal máxima (W) y factor de pico de arranque
# (motores/compresores tiran más al arrancar que en régimen estable)
# ============================================================
if "electrodomesticos" not in st.session_state:
    st.session_state.electrodomesticos = {
        "Lavaplatos":     {"nominal": 2300, "pico": 1.0},
        "Lavadora":       {"nominal": 2100, "pico": 1.0},
        "Plancha":        {"nominal": 2600, "pico": 1.0},
        "Aire Salón":     {"nominal": 1100, "pico": 1.3},
        "Aire Javier":    {"nominal": 1100, "pico": 1.3},
        "Aire Trastero":  {"nominal": 900,  "pico": 1.3},
        "Aire Laura":     {"nominal": 900,  "pico": 1.3},
        "Nevera":         {"nominal": 130,  "pico": 3.0},
    }

electrodomesticos = st.session_state.electrodomesticos

# ============================================================
# BARRA LATERAL: gestión dinámica de aparatos + modo de cálculo
# ============================================================
with st.sidebar:
    st.header("⚙️ Configuración")

    modo_pico = st.toggle(
        "Simular picos de arranque",
        value=False,
        help="Motores y compresores (AC, frigorífico) consumen más al arrancar que en régimen estable."
    )

    st.markdown("---")
    st.subheader("➕ Añadir electrodoméstico")
    with st.form("nuevo_aparato", clear_on_submit=True):
        nombre_nuevo = st.text_input("Nombre")
        potencia_nueva = st.number_input("Potencia nominal (W)", min_value=1, step=10)
        pico_nuevo = st.number_input("Factor de pico al arranque", min_value=1.0, max_value=5.0, value=1.0, step=0.1)
        if st.form_submit_button("Añadir") and nombre_nuevo:
            electrodomesticos[nombre_nuevo] = {"nominal": potencia_nueva, "pico": pico_nuevo}
            st.rerun()

    st.markdown("---")
    st.subheader("➖ Eliminar electrodoméstico")
    if electrodomesticos:
        a_eliminar = st.selectbox("Selecciona", list(electrodomesticos.keys()))
        if st.button("Eliminar"):
            del electrodomesticos[a_eliminar]
            st.rerun()

# ============================================================
# INTERRUPTORES
# ============================================================
st.subheader("🔌 Interruptores de los Electrodomésticos")
st.write("Enciende o apaga los aparatos para simular la carga simultánea:")

potencia_total = 0
aparatos_activos = []

col1, col2 = st.columns(2)
for i, (aparato, datos) in enumerate(electrodomesticos.items()):
    columna = col1 if i % 2 == 0 else col2
    with columna:
        encendido = st.toggle(f"{aparato} ({datos['nominal']} W)", key=f"toggle_{aparato}")
        if encendido:
            consumo = datos["nominal"] * (datos["pico"] if modo_pico else 1.0)
            potencia_total += consumo
            aparatos_activos.append((aparato, consumo))

st.markdown("---")

# ============================================================
# PANEL DE RESULTADOS
# ============================================================
st.subheader("📊 Estado de la Red Doméstica")

porcentaje_carga = min(potencia_total / LIMITE_CONTRATADO, 1.0)

if potencia_total > LIMITE_CONTRATADO:
    st.error("🚨 ¡ALERTA ICP: SOBRECARGA EN LA RED!")
    st.metric(
        label="Potencia Activa Total",
        value=f"{potencia_total:.0f} W",
        delta=f"+{potencia_total - LIMITE_CONTRATADO:.0f} W (Excedido)",
        delta_color="inverse"
    )
else:
    st.success("✅ Red Eléctrica Estable y Segura")
    st.metric(
        label="Potencia Activa Total",
        value=f"{potencia_total:.0f} W",
        delta=f"{LIMITE_CONTRATADO - potencia_total:.0f} W disponibles",
        delta_color="normal"
    )

st.progress(porcentaje_carga)

if modo_pico:
    st.caption("⚡ Modo pico de arranque activo: los motores/compresores se calculan a su consumo máximo instantáneo.")

# ============================================================
# DESGLOSE
# ============================================================
with st.expander("🔍 Ver aparatos activos"):
    if aparatos_activos:
        for aparato, consumo in aparatos_activos:
            st.write(f"- **{aparato}**: {consumo:.0f} W")
    else:
        st.write("Ningún aparato encendido.")

with st.expander("📋 Ver base de datos completa"):
    st.json(electrodomesticos)