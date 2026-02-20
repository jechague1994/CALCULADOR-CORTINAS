import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Grupo Magallan - Precios", layout="wide")

# Gestión del Logo y Título
archivo_logo = "logo_magallan.png"
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(archivo_logo):
        st.image(archivo_logo, width=150)
with col2:
    st.title("Grupo Magallan: Lista de Precios")

# --- BARRA LATERAL: CONTROL DEL DÓLAR ---
with st.sidebar:
    st.header("💵 Mercado")
    # PRECIO ACTUALIZADO A 1486
    usd_blue = st.number_input("Cotización Dólar (ARS):", min_value=1.0, value=1486.0, step=1.0)
    st.divider()
    st.info(f"Tipo de cambio: $ {usd_blue:,.2f}")

# --- BUSCADOR DE PRODUCTOS ---
st.subheader("🔍 Buscador de Productos")
archivo_precios = "precios.xlsx"

if os.path.exists(archivo_precios):
    try:
        # skiprows=2 para empezar a leer desde la fila 3 (donde están tus títulos)
        df = pd.read_excel(archivo_precios, skiprows=2)
        
        # Limpieza de nombres de columnas
        df.columns = df.columns.str.strip()
        
        if 'Producto' in df.columns and 'Precio' in df.columns:
            # Entrada de búsqueda
            busqueda = st.text_input("Buscar producto por nombre:")
            
            # Conversión de moneda
            df['Precio USD'] = pd.to_numeric(df['Precio'], errors='coerce')
            df['Precio ARS ($)'] = df['Precio USD'] * usd_blue
            
            # Filtrado por búsqueda
            if busqueda:
                df_filtrado = df[df['Producto'].astype(str).str.contains(busqueda, case=False, na=False)]
            else:
                df_filtrado = df

            # Formateo de visualización
            df_mostrar = df_filtrado.copy()
            df_mostrar['Precio USD'] = df_mostrar['Precio USD'].map('U$D {:,.2f}'.format)
            df_mostrar['Precio ARS ($)'] = df_mostrar['Precio ARS ($)'].map('$ {:,.2f}'.format)
            
            # Columnas a mostrar
            columnas = ['Producto', 'Precio USD', 'Precio ARS ($)']
            if 'Unidad' in df.columns:
                columnas.append('Unidad')

            st.dataframe(df_mostrar[columnas], use_container_width=True, hide_index=True)
            
        else:
            st.error("No se encontraron las columnas 'Producto' y 'Precio' en la fila 3 del Excel.")
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.warning("No se detectó el archivo 'precios.xlsx' en la carpeta.")