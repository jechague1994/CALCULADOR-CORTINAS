import streamlit as st
import os

# --- DATOS TÉCNICOS ---
TABLILLAS = {
    "Tablilla Ciega": {"peso": 14, "familia": "acero"},
    "Tablilla Microperforada": {"peso": 12, "familia": "acero"},
    "Tablilla Americana": {"peso": 16, "familia": "acero"},
    "Acero Inyectado 95mm": {"peso": 16, "familia": "acero"},
    "Acero Inyectado 125mm": {"peso": 16, "familia": "acero"},
    "Aluminio Lama 55mm": {"peso": 5, "eje": "70mm", "guias": "Específicas Alu", "familia": "alu55"},
    "Aluminio Lama 77mm": {"peso": 5, "eje": "101mm", "guias": "Específicas Alu", "familia": "alu77"}
}

def recomendar_motor(tipo, m2, usos):
    familia = TABLILLAS[tipo]["familia"]
    if familia == "alu55": return ["Motor Tubular 60"]
    if familia == "alu77": return ["Motor Tubular 140"]
    
    # Lógica de selección por uso y superficie
    if usos <= 7:
        if m2 <= 11: return ["Motor Tubular 140"]
        if m2 <= 18: return ["Motor Paralelo 600"]
        elif m2 <= 28: return ["Motor Paralelo 800"]
        elif m2 <= 32: return ["Motor Paralelo 1000"]
        elif m2 <= 42: return ["Motor Paralelo 1500"]
        return ["Consultar industrial"]
    elif 8 <= usos <= 13:
        if m2 <= 14: return ["Sb 250m", "Tb 250m"]
        if m2 <= 18: return ["Sb 300m", "Tb 320m"]
        if m2 <= 22: return ["SB 350m"]
        if m2 <= 28: return ["Tb 400m", "Sb 400m"]
        if m2 <= 38: return ["Tb 500m"]
        return ["Tb 800m"]
    else:
        if m2 <= 18: return ["Sb 250t", "Tb 250t"]
        if m2 <= 22: return ["Sb 300t", "Tb 320t"]
        if m2 <= 26: return ["Sb 350t"]
        if m2 <= 32: return ["Tb 400t", "Sb 400t"]
        if m2 <= 42: return ["Tb 500t"]
        return ["Tb 800t"]

def calcular_estructura_acero(ancho_m, alto_m, tipo_tablilla):
    # REGLA MAGALLAN: Lama 125mm -> Eje mínimo 152mm
    if tipo_tablilla == "Acero Inyectado 125mm":
        if ancho_m < 8 and alto_m <= 3: 
            return "Eje 152mm (Mínimo p/ Lama 125)", "Guías 80x60mm"
        elif ancho_m >= 8:
            return "Eje 250mm", "Guías 150x60mm"
        return "Eje 200mm", "Guías 100x60mm"

    # Reglas estándar para acero
    if ancho_m < 5 and alto_m <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho_m < 6 and alto_m <= 3: return "Eje 127mm", "Guías 80x60mm"
    if ancho_m < 7 and alto_m <= 3: return "Eje 152mm", "Guías 80x60mm"
    if ancho_m < 8 and alto_m <= 3: return "Eje 200mm", "Guías 100x60mm"
    return "Eje 250mm", "Guías 150x60mm"

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Grupo Magallan", layout="wide")

archivo_logo = "logo_magallan.png"
logo_existe = os.path.exists(archivo_logo)

# Encabezado con Logo
col1, col2 = st.columns([1, 4])
with col1:
    if logo_existe:
        st.image(archivo_logo, width=150)
    else:
        st.info("Logo no detectado")
with col2:
    st.title("Grupo Magallan: Calculador Técnico")

# --- ENTRADA DE DATOS ---
with st.sidebar:
    st.header("⚙️ Medidas (Mts)")
    tipo_sel = st.selectbox("Tipo de Tablilla:", list(TABLILLAS.keys()))
    ancho_m = st.number_input("Ancho Vano (m):", 0.1, 20.0, 4.0)
    alto_v = st.number_input("Alto Vano (m):", 0.1, 20.0, 3.0)
    usos_dia = st.number_input("Accionamientos diarios:", 1, 100, 5)
    enrollar = st.checkbox("Incluir excedente de enrollado", True)

# --- CÁLCULOS ---
fam = TABLILLAS[tipo_sel]["familia"]
extra = (0.30 if fam == "alu55" else 0.40) if enrollar else 0
alto_f = alto_v + extra
m2 = ancho_m * alto_f
peso = m2 * TABLILLAS[tipo_sel]["peso"]

if "alu" in fam:
    eje, guias = (TABLILLAS[tipo_sel]["eje"], TABLILLAS[tipo_sel]["guias"])
else:
    eje, guias = calcular_estructura_acero(ancho_m, alto_v, tipo_sel)

motores = recomendar_motor(tipo_sel, m2, usos_dia)

# --- RESULTADOS EN PANTALLA ---
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Superficie Total", f"{m2:.2f} m²")
c2.metric("Peso Estimado", f"{peso:.1f} kg")
c3.info(f"*Eje Sugerido:*\n{eje}")
c4.info(f"*Guías Sugeridas:*\n{guias}")

st.subheader("🚀 Motorización Recomendada")
for m in motores:
    st.success(f"Opción: {m}")