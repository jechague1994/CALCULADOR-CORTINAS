import streamlit as st
from fpdf import FPDF
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

def calcular_estructura_acero(ancho_m, alto_m):
    if ancho_m < 5 and alto_m <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho_m < 6 and alto_m <= 3: return "Eje 127mm", "Guías 80x60mm"
    if ancho_m < 7 and alto_m <= 3: return "Eje 152mm", "Guías 80x60mm"
    if ancho_m < 8 and alto_m <= 3: return "Eje 200mm", "Guías 100x60mm"
    return "Eje 250mm", "Guías 150x60mm"

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grupo Magallan", layout="wide")

# Lógica del Logo
archivo_logo = "logo_magallan.png"
logo_existe = os.path.exists(archivo_logo)

# Encabezado
col1, col2 = st.columns([1, 4])
with col1:
    if logo_existe:
        st.image(archivo_logo, width=150)
    else:
        st.error("Logo no hallado")
with col2:
    st.title("Grupo Magallan: Calculador Técnico")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Entrada (Mts)")
    tipo = st.selectbox("Tablilla:", list(TABLILLAS.keys()))
    ancho = st.number_input("Ancho (m):", 0.1, 20.0, 4.0)
    alto_v = st.number_input("Alto Vano (m):", 0.1, 20.0, 3.0)
    usos = st.number_input("Usos/Día:", 1, 50, 5)
    enrollar = st.checkbox("Sumar enrollado", True)

# --- CÁLCULOS ---
fam = TABLILLAS[tipo]["familia"]
extra = (0.30 if fam == "alu55" else 0.40) if enrollar else 0
alto_f = alto_v + extra
m2 = ancho * alto_f
peso = m2 * TABLILLAS[tipo]["peso"]
eje, guias = (TABLILLAS[tipo]["eje"], TABLILLAS[tipo]["guias"]) if "alu" in fam else calcular_estructura_acero(ancho, alto_v)
motores = recomendar_motor(tipo, m2, usos)

# --- RESULTADOS ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Superficie", f"{m2:.2f} m²")
k2.metric("Peso", f"{peso:.1f} kg")
k3.info(f"Eje: {eje}")
k4.info(f"Guías: {guias}")

st.subheader("🚀 Motores")
for m in motores: st.success(m)

# --- PDF ---
if st.button("Generar PDF"):
    pdf = FPDF()
    pdf.add_page()
    if logo_existe:
        pdf.image(archivo_logo, 10, 8, 30)
        pdf.set_x(45)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "GRUPO MAGALLAN - FICHA TECNICA", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
    resumen = [
        ("Material", tipo), ("Vano", f"{ancho}x{alto_v}m"),
        ("Alto Final", f"{alto_f}m"), ("Superficie", f"{m2:.2f}m2"),
        ("Eje", eje), ("Guias", guias), ("Motores", ", ".join(motores))
    ]
    
    for c, v in resumen:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 8, c, 1)
        pdf.set_font("Arial", size=10)
        pdf.cell(100, 8, str(v), 1, 1)
    
    st.download_button("📥 Descargar", pdf.output(dest='S').encode('latin-1'), "Ficha_Magallan.pdf")