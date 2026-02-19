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
        recomendaciones = []
        if m2 <= 11: recomendaciones.append("Motor Tubular 140")
        if m2 <= 18: recomendaciones.append("Motor Paralelo 600")
        elif m2 <= 28: recomendaciones.append("Motor Paralelo 800")
        elif m2 <= 32: recomendaciones.append("Motor Paralelo 1000")
        elif m2 <= 42: recomendaciones.append("Motor Paralelo 1500")
        else: recomendaciones.append("Consultar motor industrial especial")
        return recomendaciones
    elif 8 <= usos <= 13:
        if m2 <= 14: return ["Sb 250m", "Tb 250m"]
        if m2 <= 18: return ["Sb 300m", "Tb 320m"]
        if m2 <= 22: return ["SB 350m"]
        if m2 <= 28: return ["Tb 400m", "Sb 400m"]
        if m2 <= 38: return ["Tb 500m"]
        if m2 <= 64: return ["Tb 800m"]
        return ["Consultar modelo Monofásico potente"]
    else:
        if m2 <= 18: return ["Sb 250t", "Tb 250t"]
        if m2 <= 22: return ["Sb 300t", "Tb 320t"]
        if m2 <= 26: return ["Sb 350t"]
        if m2 <= 32: return ["Tb 400t", "Sb 400t"]
        if m2 <= 42: return ["Tb 500t"]
        if m2 <= 64: return ["Tb 800t"]
        return ["Consultar modelo Trifásico potente"]

def calcular_estructura_acero(ancho_m, alto_m):
    if ancho_m < 5 and alto_m <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho_m < 6 and alto_m <= 3: return "Eje 127mm", "Guías 80x60mm"
    if ancho_m < 7 and alto_m <= 3: return "Eje 152mm", "Guías 80x60mm"
    if ancho_m < 8 and alto_m <= 3: return "Eje 200mm", "Guías 100x60mm"
    return "Eje 250mm", "Guías 150x60mm"

# --- INTERFAZ ---
st.set_page_config(page_title="Grupo Magallan - Configurador", layout="wide")

# Reemplazo del Título y Logo
col_logo, col_tit = st.columns([1, 5])
with col_logo:
    # Intenta cargar el nuevo logo. Si no existe, muestra un texto.
    if os.path.exists("logo_magallan.png"):
        st.image("logo_magallan.png", width=100)
    else:
        st.write("🟦") # Icono temporal si falta el archivo
with col_tit:
    st.title("Grupo Magallan: Calculador Técnico")

with st.sidebar:
    st.header("⚙️ Entrada de Medidas (Mts)")
    tipo_sel = st.selectbox("Tipo de Tablilla:", list(TABLILLAS.keys()))
    ancho_m = st.number_input("Ancho del Vano (metros)", min_value=0.1, value=4.0, step=0.1)
    alto_m = st.number_input("Alto del Vano (metros)", min_value=0.1, value=3.0, step=0.1)
    usos_dia = st.number_input("Accionamientos al día:", min_value=1, value=5)
    agregar_enrollado = st.checkbox("Agregar excedente de enrollado", value=True)

# Lógica de cálculo
familia = TABLILLAS[tipo_sel]["familia"]
excedente_m = 0
if agregar_enrollado:
    excedente_m = 0.30 if familia == "alu55" else 0.40

alto_final_m = alto_m + excedente_m
superficie_m2 = ancho_m * alto_final_m
peso_t = superficie_m2 * TABLILLAS[tipo_sel]["peso"]

if "alu" in familia:
    eje_f, guias_f = (TABLILLAS[tipo_sel]["eje"], TABLILLAS[tipo_sel]["guias"])
else:
    eje_f, guias_f = calcular_estructura_acero(ancho_m, alto_m)

motores = recomendar_motor(tipo_sel, superficie_m2, usos_dia)

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Superficie Total", f"{superficie_m2:.2f} m²")
c2.metric("Peso del Paño", f"{peso_t:.1f} kg")
c3.info(f"*Eje:* {eje_f}")
c4.info(f"*Guías:* {guias_f}")

st.subheader("🚀 Motorización Seleccionada")
for m in motores:
    st.success(f"Motor: {m}")

# --- PDF ---
if st.button("Generar Ficha para Taller"):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Logo en la esquina del PDF
        if os.path.exists("logo_magallan.png"):
            pdf.image("logo_magallan.png", 10, 8, 25)
            pdf.set_x(40)
        
        pdf.set_font("Arial", "B", 20)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(150, 15, "GRUPO MAGALLAN", ln=True, align='L')
        pdf.ln(10)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "DETALLE TÉCNICO DE FABRICACIÓN", ln=True, align='C')
        pdf.ln(5)

        data = [
            ("Tipo de Lama", tipo_sel),
            ("Medida Vano", f"{ancho_m:.2f} x {alto_m:.2f} mts"),
            ("Excedente", f"+ {excedente_m:.2f} mts"),
            ("Alto Final", f"{alto_final_m:.2f} mts"),
            ("Superficie", f"{superficie_m2:.2f} m2"),
            ("Uso Diario", f"{usos_dia} accionamientos"),
            ("Eje", eje_f),
            ("Guías", guias_f),
            ("Motores", ", ".join(motores))
        ]

        for label, val in data:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(70, 10, label, 1)
            pdf.set_font("Arial", size=11)
            pdf.cell(120, 10, str(val), 1, 1)

        pdf_bytes = bytes(pdf.output())
        st.download_button("📥 Descargar PDF", pdf_bytes, "Ficha_Magallan.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")