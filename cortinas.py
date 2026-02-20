import streamlit as st
import pandas as pd
import os

# --- 1. DATOS TÉCNICOS (TU CALCULADOR ORIGINAL) ---
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

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Grupo Magallan", layout="wide")

# Logo y Título
archivo_logo = "logo_magallan.png"
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(archivo_logo):
        st.image(archivo_logo, width=150)
with col2:
    st.title("Grupo Magallan: Gestión Técnica y Comercial")

# --- 3. SIDEBAR (CONTROLES) ---
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
    # Lógica de cálculo técnico
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

    st.divider()
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Superficie Total", f"{m2:.2f} m²")
    res2.metric("Peso Estimado", f"{peso:.1f} kg")
    res3.info(f"*Eje:*\n{eje}")
    res4.info(f"*Guías:*\n{guias}")
    
    st.subheader("🚀 Motores Sugeridos")
    for m in motores:
        st.success(f"Opción: {m}")

with tab_precios:
    st.subheader(f"🔍 Buscador de Productos (Dólar: ${usd_blue})")
    
    # Nombre exacto de tu archivo (asegúrate que esté en GitHub con este nombre)
    archivo_precios = "precios.xlsx"
    
    if os.path.exists(archivo_precios):
        try:
            # LEER DESDE FILA 3 (skiprows=2) como vimos en tu foto
            df = pd.read_excel(archivo_precios, skiprows=2)
            df.columns = df.columns.str.strip() # Limpiar espacios en títulos
            
            if 'Producto' in df.columns and 'Precio' in df.columns:
                busqueda = st.text_input("Buscar producto por nombre:")
                
                # Conversión de moneda
                df['Precio'] = pd.to_numeric(df['Precio'], errors='coerce')
                df['Precio ARS ($)'] = df['Precio'] * usd_blue
                
                # Filtrado
                if busqueda:
                    df_final = df[df['Producto'].astype(str).str.contains(busqueda, case=False, na=False)]
                else:
                    df_final = df
                
                # Formateo visual
                df_vis = df_final.copy()
                df_vis['Precio USD'] = df_vis['Precio'].map('U$D {:,.2f}'.format)
                df_vis['Precio ARS ($)'] = df_vis['Precio ARS ($)'].map('$ {:,.2f}'.format)
                
                # Columnas a mostrar
                cols_mostrar = ['Producto', 'Precio USD', 'Precio ARS ($)']
                if 'Unidad' in df.columns:
                    cols_mostrar.append('Unidad')
                
                st.dataframe(df_vis[cols_mostrar], use_container_width=True, hide_index=True)
            else:
                st.error("No se encuentran las columnas 'Producto' y 'Precio' en la fila 3 del Excel.")
        except Exception as e:
            st.error(f"Ocurrió un error al leer el Excel: {e}")
    else:
        st.warning(f"⚠️ No se encontró el archivo '{archivo_precios}'. Asegúrate de que el nombre sea exacto y esté subido a GitHub.")