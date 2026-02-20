import streamlit as st
import pandas as pd
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
    fam = TABLILLAS[tipo]["familia"]
    if fam == "alu55": return ["Motor Tubular 60"]
    if fam == "alu77": return ["Motor Tubular 140"]
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

def calcular_estructura(ancho, alto, tipo):
    if tipo == "Acero Inyectado 125mm":
        return ("Eje 152mm (Mín p/ 125)" if ancho < 8 else "Eje 250mm"), "Guías 150x60mm"
    if ancho < 5 and alto <= 3: return "Eje redondo 101mm", "Guías 60x50mm"
    if ancho < 7 and alto <= 3: return "Eje 152mm", "Guías 80x60mm"
    return "Eje 200mm", "Guías 100x60mm"

# --- INTERFAZ ---
st.set_page_config(page_title="Grupo Magallan", layout="wide")

# Sidebar
with st.sidebar:
    st.header("💵 Mercado")
    usd_blue = st.number_input("Dólar Hoy (ARS):", 1.0, 3000.0, 1450.0)
    st.divider()
    st.header("⚙️ Medidas")
    tipo_sel = st.selectbox("Tablilla:", list(TABLILLAS.keys()))
    ancho_m = st.number_input("Ancho (m):", 0.1, 20.0, 4.0)
    alto_v = st.number_input("Alto (m):", 0.1, 20.0, 3.0)
    usos = st.number_input("Usos/día:", 1, 100, 5)
    enrollar = st.checkbox("Sumar enrollado", True)

# Cálculos Técnicos
fam = TABLILLAS[tipo_sel]["familia"]
m2 = ancho_m * (alto_v + (0.3 if fam=="alu55" else 0.4) if enrollar else alto_v)
peso = m2 * TABLILLAS[tipo_sel]["peso"]
eje, guias = (TABLILLAS[tipo_sel]["eje"], TABLILLAS[tipo_sel]["guias"]) if "alu" in fam else calcular_estructura(ancho_m, alto_v, tipo_sel)

# --- PESTAÑAS ---
t1, t2 = st.tabs(["📋 Técnico", "💰 Precios y Cotización"])

with t1:
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Superficie", f"{m2:.2f} m²")
    col_b.metric("Peso", f"{peso:.1f} kg")
    col_c.info(f"*Eje:* {eje}\n\n*Guías:* {guias}")
    st.subheader("🚀 Motores Sugeridos")
    for m in recomendar_motor(tipo_sel, m2, usos): st.success(m)

with t2:
    st.subheader(f"🔍 Consulta de Precios (Dólar: ${usd_blue})")
    if os.path.exists("precios.xlsx"):
        # LEER EXCEL: Saltamos las primeras 2 filas porque tus títulos están en la fila 3
        df = pd.read_excel("precios.xlsx", skiprows=2)
        df.columns = df.columns.str.strip() # Limpiamos espacios en nombres de columnas

        if 'Producto' in df.columns and 'Precio' in df.columns:
            busqueda = st.text_input("Buscar producto:")
            
            # Filtro
            if busqueda:
                df = df[df['Producto'].astype(str).str.contains(busqueda, case=False, na=False)]
            
            # Cálculos de moneda
            df['Precio USD'] = pd.to_numeric(df['Precio'], errors='coerce')
            df['Total ARS ($)'] = df['Precio USD'] * usd_blue
            
            # --- NUEVA FUNCIÓN: Cotizador rápido ---
            st.write("---")
            st.caption("Selecciona un producto para calcular costo total basado en las medidas de la izquierda:")
            sel_prod = st.selectbox("Calcular para:", ["Ninguno"] + df['Producto'].tolist())
            
            if sel_prod != "Ninguno":
                row = df[df['Producto'] == sel_prod].iloc[0]
                precio_u = row['Precio USD']
                unidad = str(row['Unidad']).upper() if 'Unidad' in df.columns else "UN"
                
                # Si es MT2, multiplicamos por la superficie calculada
                cantidad = m2 if "MT2" in unidad else 1
                total_final = precio_u * cantidad * usd_blue
                
                c1, c2 = st.columns(2)
                c1.warning(f"Costo Unitario: USD {precio_u:.2f}")
                c2.error(f"TOTAL ESTIMADO ({unidad}): $ {total_final:,.2f} ARS")

            st.write("---")
            # Mostrar tabla formateada
            df_vis = df.copy()
            df_vis['Precio USD'] = df_vis['Precio USD'].map('{:,.2f}'.format)
            df_vis['Total ARS ($)'] = df_vis['Total ARS ($)'].map('$ {:,.2f}'.format)
            st.dataframe(df_vis[['Producto', 'Precio USD', 'Total ARS ($)', 'Unidad']], use_container_width=True, hide_index=True)
        else:
            st.error("Asegúrate de que en la fila 3 del Excel digan exactamente: 'Producto', 'Precio' y 'Unidad'.")
    else:
        st.warning("No se encontró el archivo 'precios.xlsx'.")