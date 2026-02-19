import streamlit as st
from fpdf import FPDF

# --- LÓGICA DE CÁLCULO ---
def calcular_despiece(ancho, alto):
    margen_guia = 35    
    descuento_eje = 50  
    alto_tablilla = 80  
    
    ancho_tab = ancho + (margen_guia * 2) - 10
    cant_tab = int(alto / alto_tablilla) + 2
    l_guias = alto + 150
    l_eje = ancho - descuento_eje

    return {
        "Ancho Tablilla (mm)": ancho_tab,
        "Cantidad Tablillas": cant_tab,
        "Largo Guías (mm)": l_guias,
        "Largo Eje (mm)": l_eje
    }

# --- INTERFAZ ---
st.set_page_config(page_title="Calculador Cortinas")
st.title("🛠️ Calculador de Cortinas Metálicas")

col1, col2 = st.columns(2)
with col1:
    ancho_v = st.number_input("Ancho Vano (mm)", min_value=100, value=2500)
with col2:
    alto_v = st.number_input("Alto Vano (mm)", min_value=100, value=2000)

if st.button("Calcular y Generar PDF"):
    datos = calcular_despiece(ancho_v, alto_v)
    
    st.subheader("Resultados:")
    for k, v in datos.items():
        st.write(f"*{k}:* {v}")

    # --- GENERACIÓN DE PDF ---
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ORDEN DE FABRICACION", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(190, 10, f"Medidas del Vano: {ancho_v} x {alto_v} mm", ln=True)
        pdf.ln(5)

        for concepto, valor in datos.items():
            pdf.cell(95, 10, str(concepto), 1)
            pdf.cell(95, 10, str(valor), 1, 1)

        # Esta es la forma más segura de obtener los datos del PDF en Python 3.14
        pdf_output = pdf.output()
        pdf_bytes = bytes(pdf_output)

        st.download_button(
            label="📥 DESCARGAR PDF",
            data=pdf_bytes,
            file_name="despiece_cortina.pdf",
            mime="application/pdf"
        )
        st.success("¡PDF generado con éxito!")
    except Exception as e:
        st.error(f"Error al crear el PDF: {e}")