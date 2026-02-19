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

def calcular_estructura_acero(ancho_m, alto_m, tipo_tablilla):
    # Regla especial para Inyectada 125mm: Eje mínimo 152mm
    if tipo_tablilla == "Acero Inyectado 125mm":
        if ancho_m < 8 and alto_m <= 3: 
            return "Eje 152mm (Mínimo p/ Lama 125)", "Guías 80x60mm"
        elif ancho_m >= 8:
            return "Eje 250mm", "Guías 150x60mm"
        else:
            return "Eje 200mm", "Guías 100x60mm"

    # Reglas estándar para el resto
    if ancho_m < 5 and alto_m <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho_m < 6 and alto_m <= 3: return "Eje 127mm", "Guías 80x60mm"
    if ancho_m < 7 and alto_m <= 3: return "Eje 152mm", "Guías 80x60mm"
    if ancho_m < 8 and alto_m <= 3: return "Eje 200mm", "Guías 100x60mm"
    return "Eje 250mm", "Guías 150x60mm"

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Grupo Magallan - Calculador", layout="wide")

# Lógica del Logo
archivo_logo = "logo_magallan.png"
logo_existe = os.path.exists(archivo_logo)

# Encabezado
col1, col2 = st.columns([1, 4])
with col1:
    if logo_existe:
        st.image(archivo_logo, width=150)
    else:
        st.error("Archivo logo_magallan.png no encontrado")

with col2:
    st.title("Grupo Magallan: Calculador Técnico")

# --- SIDEBAR (ENTRADA DE DATOS) ---
with st.sidebar:
    st.header("⚙️ Medidas en Metros")
    tipo_sel = st.selectbox("Tipo de Tablilla:", list(TABLILLAS.keys()))
    ancho_m = st.number_input("Ancho del Vano (m):", min_value=0.1, value=4.0, step=0.1)
    alto_v = st.number_input("Alto del Vano (m):", min_value=0.1, value=3.0, step=0.1)
    usos_dia = st.number_input("Accionamientos al día:", min_value=1, value=5)
    agregar_enrollado = st.checkbox("Incluir excedente de enrollado", value=True)

# --- CÁLCULOS TÉCNICOS ---
familia = TABLILLAS[tipo_sel]["familia"]
excedente_m = (0.30 if familia == "alu55" else 0.40) if agregar_enrollado else 0
alto_final_m = alto_v + excedente_m
superficie_m2 = ancho_m * alto_final_m
peso_t = superficie_m2 * TABLILLAS[tipo_sel]["peso"]

# Determinación de Eje y Guías
if "alu" in familia:
    eje_f, guias_f = (TABLILLAS[tipo_sel]["eje"], TABLILLAS[tipo_sel]["guias"])
else:
    eje_f, guias_f = calcular_estructura_acero(ancho_m, alto_v, tipo_sel)

motores = recomendar_motor(tipo_sel, superficie_m2, usos_dia)

# --- PANEL DE RESULTADOS ---
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Superficie Real", f"{superficie_m2:.2f} m²")
c2.metric("Peso Estimado", f"{peso_t:.1f} kg")
c3.info(f"*Eje:*\n{eje_f}")
c4.info(f"*Guías:*\n{guias_f}")

st.subheader("🚀 Motorización Recomendada")
for m in motores:
    st.success(f"Opción: {m}")

# --- GENERACIÓN DE PDF ---
if st.button("Generar Ficha de Fabricación"):
    try:
        pdf = FPDF()
        pdf.add_page()
        if logo_existe:
            pdf.image(archivo_logo, 10, 8, 30)
            pdf.set_x(45)
        
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 15, "GRUPO MAGALLAN - ORDEN TÉCNICA", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(0, 0, 0)
        
        datos = [
            ("Lama Seleccionada", tipo_sel),
            ("Medida Vano", f"{ancho_m:.2f} x {alto_v:.2f} m"),
            ("Superficie Total", f"{superficie_m2:.2f} m2"),
            ("Peso del Paño", f"{peso_t:.1f} kg"),
            ("Uso Diario", f"{usos_dia} accionamientos"),
            ("EJE REQUERIDO", eje_f.upper()),
            ("GUÍAS REQUERIDAS", guias_f.upper()),
            ("MOTORES SUGERIDOS", ", ".join(motores))
        ]

        for etiqueta, valor in datos:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(60, 9, etiqueta, 1)
            pdf.set_font("Arial", size=10)
            pdf.cell(130, 9, str(valor), 1, 1)

        # Usamos un método seguro para descargar en Streamlit Cloud
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Descargar PDF", pdf_output, f"Orden_{tipo_sel}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Error al generar el documento: {e}")