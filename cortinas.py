import streamlit as st
from fpdf import FPDF

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

def calcular_estructura_acero(ancho_mm, alto_mm):
    ancho = ancho_mm / 1000
    alto = alto_mm / 1000
    
    if ancho < 5 and alto <= 3:
        return "Eje redondo 101mm", "Guías 60x50mm"
    elif ancho < 6 and alto <= 3:
        return "Eje 127mm", "Guías 80x60mm"
    elif ancho < 7 and alto <= 3:
        return "Eje 152mm", "Guías 80x60mm"
    elif ancho < 8 and alto <= 3:
        return "Eje 200mm", "Guías 100x60mm"
    elif ancho >= 8:
        return "Eje 250mm", "Guías 150x60mm"
    else:
        # Si supera los 3mts de alto pero no los 8 de ancho, escalamos al siguiente nivel de seguridad
        return "Eje 152mm (Reforzado por altura)", "Guías 80x60mm"

def recomendar_motor(tipo, m2):
    familia = TABLILLAS[tipo]["familia"]
    if familia == "alu55": return ["Motor Tubular 60"]
    if familia == "alu77": return ["Motor Tubular 140"]
    
    recomendaciones = []
    if m2 <= 11: recomendaciones.append("Motor Tubular 140")
    if m2 <= 18: recomendaciones.append("Motor Paralelo 600")
    elif m2 <= 28: recomendaciones.append("Motor Paralelo 800")
    elif m2 <= 32: recomendaciones.append("Motor Paralelo 1000")
    elif m2 <= 42: recomendaciones.append("Motor Paralelo 1500")
    else: recomendaciones.append("Consultar motor industrial (+42m2)")
    return recomendaciones

# --- INTERFAZ ---
st.set_page_config(page_title="Configurador Técnico de Cortinas", layout="wide")
st.title("🏭 Sistema de Configuración de Estructura y Motorización")

with st.sidebar:
    st.header("Entrada de Datos")
    tipo_sel = st.selectbox("Tipo de Tablilla:", list(TABLILLAS.keys()))
    ancho_v = st.number_input("Ancho Vano (mm)", min_value=100, value=4500, step=10)
    alto_v = st.number_input("Alto Vano (mm)", min_value=100, value=2500, step=10)
    agregar_enrollado = st.checkbox("Agregar excedente para enrollar", value=True)

# Lógica de Altura y Superficie
familia = TABLILLAS[tipo_sel]["familia"]
excedente = 0
if agregar_enrollado:
    excedente = 300 if familia == "alu55" else 400

alto_f = alto_v + excedente
m2 = (ancho_v / 1000) * (alto_f / 1000)
peso_t = m2 * TABLILLAS[tipo_sel]["peso"]

# Selección de Eje y Guías
if "alu" in familia:
    eje_final = TABLILLAS[tipo_sel]["eje"]
    guias_final = TABLILLAS[tipo_sel]["guias"]
else:
    eje_final, guias_final = calcular_estructura_acero(ancho_v, alto_v)

motores = recomendar_motor(tipo_sel, m2)

# Visualización de Resultados
st.divider()
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Superficie Real", f"{m2:.2f} m²")
with c2:
    st.metric("Peso Estimado", f"{peso_t:.1f} kg")
with c3:
    st.info(f"*Eje:* {eje_final}")
with c4:
    st.info(f"*Guías:* {guias_final}")

st.subheader("🚀 Motorización Sugerida")
st.write(f"Para una cortina de {tipo_sel} con {m2:.2f} m²:")
cols_m = st.columns(len(motores) if motores else 1)
for i, m in enumerate(motores):
    cols_m[i].success(f"✅ {m}")

# --- GENERACIÓN DE PDF ---
if st.button("Descargar Ficha Técnica Completa"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ORDEN DE FABRICACION Y DESPIECE", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=11)
        pdf.set_fill_color(240, 240, 240)
        
        datos = [
            ("Material de Tablilla", tipo_sel),
            ("Ancho del Vano", f"{ancho_v} mm"),
            ("Alto del Vano", f"{alto_v} mm"),
            ("Alto Total (+ Enrollado)", f"{alto_f} mm"),
            ("Superficie Final", f"{m2:.2f} m2"),
            ("Peso Total Paño", f"{peso_t:.1f} kg"),
            ("EJE RECOMENDADO", eje_final.upper()),
            ("GUIAS RECOMENDADAS", guias_final.upper()),
            ("MOTORES COMPATIBLES", ", ".join(motores))
        ]
        
        for etiqueta, valor in datos:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(80, 10, etiqueta, 1, 0, 'L', True)
            pdf.set_font("Arial", size=11)
            pdf.cell(110, 10, valor, 1, 1, 'L')

        pdf_bytes = bytes(pdf.output())
        st.download_button("📥 Bajar PDF", pdf_bytes, "Orden_Fabricacion.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")