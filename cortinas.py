import streamlit as st
import pandas as pd
import os

# --- 1. DATOS TÉCNICOS (TALLER) ---
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
        elif m2 <= 18: return ["Motor Paralelo 600"]
        elif m2 <= 28: return ["Motor Paralelo 800"]
        elif m2 <= 32: return ["Motor Paralelo 1000"]
        elif m2 <= 42: return ["Motor Paralelo 1500"]
        return ["Consultar industrial"]
    elif 8 <= usos <= 13:
        if m2 <= 14: return ["Sb 250m", "Tb 250m"]
        elif m2 <= 18: return ["Sb 300m", "Tb 320m"]
        elif m2 <= 28: return ["Tb 400m", "Sb 400m"]
        return ["Tb 800m"]
    else:
        if m2 <= 18: return ["Sb 250t", "Tb 250t"]
        elif m2 <= 32: return ["Tb 400t", "Sb 400t"]
        return ["Tb 800t"]

def calcular_estructura_acero(ancho_m, alto_m, tipo_tablilla):
    if tipo_tablilla == "Acero Inyectado 125mm":
        return ("Eje 152mm (Mínimo p/ Lama 125)" if ancho_m < 8 else "Eje 250mm"), "Guías 150x60mm"
    if ancho_m < 5 and alto_m <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho_m < 7 and alto_m <= 3: return "Eje 152mm", "Guías 80x60mm"
    return "Eje 200mm", "Guías 100x60mm"

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="Grupo Magallan", layout="wide")

# Logo y Título
archivo_logo = "logo_magallan.png"
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(archivo_logo):
        st.image(archivo_logo, width=150)
with col2:
    st.title("Grupo Magallan: Gestión Técnica y Comercial")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("💵 Mercado")
    usd_blue = st.number_input("Dólar Hoy (ARS):", min_value=1.0, value=1486.0, step=1.0)
    st.divider()
    st.header("⚙️ Datos de Cortina")
    tipo_sel = st.selectbox("Tipo de Tablilla:", list(TABLILLAS.keys()))
    ancho_m = st.number_input("Ancho Vano (m):", 0.1, 20.0, 4.0)
    alto_v = st.number_input("Alto Vano (m):", 0.1, 20.0, 3.0)
    usos_dia = st.number_input("Usos por día:", 1, 100, 5)
    enrollar = st.checkbox("Sumar enrollado", True)

# --- 4. PESTAÑAS ---
tab_tec, tab_precios = st.tabs(["📋 Calculador Técnico", "💰 Lista de Precios"])

with tab_tec:
    extra = (0.30 if TABLILLAS[tipo_sel]["familia"] == "alu55" else 0.40) if enrollar else 0
    m2 = ancho_m * (alto_v + extra)
    peso = m2 * TABLILLAS[tipo_sel]["peso"]
    
    if "alu" in TABLILLAS[tipo_sel]["familia"]:
        eje, guias = (TABLILLAS[tipo_sel]["eje"], TABLILLAS[tipo_sel]["guias"])
    else:
        eje, guias = calcular_estructura_acero(ancho_m, alto_v, tipo_sel)
    
    motores = recomendar_motor(tipo_sel, m2, usos_dia)
    st.divider()
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superficie Total", f"{m2:.2f} m²")
    res2.metric("Peso Estimado", f"{peso:.1f} kg")
    res3.info(f"*Eje:*\n{eje}")
    res4.info(f"*Guías:*\n{guias}")
    st.subheader("🚀 Motores Sugeridos")
    for m in motores: st.success(f"Opción: {m}")

with tab_precios:
    st.subheader("🔍 Buscador de Productos")
    # VOLVEMOS AL NOMBRE ESTÁNDAR
    archivo_precios = "precios.xlsx" 
    
    if os.path.exists(archivo_precios):
        try:
            # Saltamos 2 filas para leer los títulos en la fila 3
            df = pd.read_excel(archivo_precios, skiprows=2)
            df.columns = df.columns.str.strip()
            
            if 'Producto' in df.columns and 'Precio' in df.columns:
                busqueda = st.text_input("Buscar por nombre o palabra clave:")
                
                # Conversión interna
                df['Precio Num'] = pd.to_numeric(df['Precio'], errors='coerce')
                df['Precio ARS ($)'] = df['Precio Num'] * usd_blue
                
                # Búsqueda flexible (contiene la palabra en cualquier posición)
                if busqueda:
                    df_final = df[df['Producto'].astype(str).str.contains(busqueda, case=False, na=False)]
                else:
                    df_final = df
                
                # Formateo y selección de columnas (Dólar oculto)
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
        st.warning(f"No se encontró el archivo '{archivo_precios}' en el repositorio.")