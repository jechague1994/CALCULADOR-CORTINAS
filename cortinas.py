import streamlit as st
import pandas as pd
import os

# --- 1. DATOS TÉCNICOS (Restaurados de tu código de taller) ---
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
    # Lógica de ejes y guías exacta de tu código
    if ancho_m < 5 and alto_m <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho_m < 6 and alto_m <= 3: return "Eje 127mm", "Guías 80x60mm"
    if ancho_m < 7 and alto_m <= 3: return "Eje 152mm", "Guías 80x60mm"
    if ancho_m < 8 and alto_m <= 3: return "Eje 200mm", "Guías 100x60mm"
    return "Eje 250mm", "Guías 150x60mm"

# --- 2. CONFIGURACIÓN APP ---
st.set_page_config(page_title="Grupo Magallan - Gestión", layout="wide")

# Sidebar
with st.sidebar:
    st.header("💵 Mercado")
    usd_blue = st.number_input("Dólar Hoy (ARS):", min_value=1.0, value=1486.0, step=1.0)
    st.divider()
    st.header("⚙️ Entrada de Medidas (Mts)")
    tipo_sel = st.selectbox("Tipo de Tablilla:", list(TABLILLAS.keys()))
    ancho_m = st.number_input("Ancho del Vano (metros)", min_value=0.1, value=4.0, step=0.1)
    alto_m = st.number_input("Alto del Vano (metros)", min_value=0.1, value=3.0, step=0.1)
    usos_dia = st.number_input("Accionamientos al día:", min_value=1, value=5)
    agregar_enrollado = st.checkbox("Agregar excedente de enrollado", value=True)

# Lógica de cálculo (Taller)
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

# --- PESTAÑAS ---
tab_tec, tab_precios = st.tabs(["📋 Calculador Técnico", "💰 Lista de Precios"])

with tab_tec:
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Superficie Total", f"{superficie_m2:.2f} m²")
    c2.metric("Peso del Paño", f"{peso_t:.1f} kg")
    c3.info(f"*Eje:*\n{eje_f}")
    c4.info(f"*Guías:*\n{guias_f}")

    st.subheader("🚀 Motorización Seleccionada")
    for m in motores:
        st.success(f"Motor: {m}")

with tab_precios:
    st.subheader("🔍 Buscador de Productos")
    archivo_precios = "precios.xlsx" 
    
    if os.path.exists(archivo_precios):
        try:
            # Leer desde fila 3 (skiprows=2)
            df = pd.read_excel(archivo_precios, skiprows=2)
            df.columns = df.columns.str.strip()
            
            if 'Producto' in df.columns and 'Precio' in df.columns:
                busqueda = st.text_input("Buscar por nombre o palabra clave:")
                
                # Conversión interna
                df['Precio Num'] = pd.to_numeric(df['Precio'], errors='coerce')
                df['Precio ARS ($)'] = df['Precio Num'] * usd_blue
                
                # Búsqueda parcial y flexible
                if busqueda:
                    df_final = df[df['Producto'].astype(str).str.contains(busqueda, case=False, na=False)]
                else:
                    df_final = df
                
                # Formateo (solo mostramos ARS y Unidad)
                df_vis = df_final.copy()
                df_vis['Precio ARS ($)'] = df_vis['Precio ARS ($)'].map('$ {:,.2f}'.format)
                
                cols_finales = ['Producto', 'Precio ARS ($)']
                if 'Unidad' in df.columns:
                    cols_finales.append('Unidad')
                
                st.dataframe(df_vis[cols_finales], use_container_width=True, hide_index=True)
            else:
                st.error("El Excel debe tener 'Producto' y 'Precio' en la fila 3.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
    else:
        st.warning(f"No se encontró el archivo '{archivo_precios}'.")