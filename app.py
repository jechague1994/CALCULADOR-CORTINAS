import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date, timedelta
import plotly.express as px
from fpdf import FPDF

# URL del logo oficial
LOGO_URL = "https://r.jina.ai/i/0586f37648354c4193568c07d3967484"

# 1. CONFIGURACIÓN DE INTERFAZ
st.set_page_config(page_title="Magallan | Gestión & Analytics", layout="wide", page_icon="🏗️")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #F4F5F7; }}
    .ticket-card {{ 
        background-color: white; padding: 15px; border-radius: 5px; 
        border-left: 10px solid #DFE1E6; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
    .status-terminado {{ border-left-color: #36B37E !important; }}
    .status-atrasado {{ border-left-color: #FF5630 !important; }}
    .status-proceso {{ border-left-color: #0052CC !important; }}
    .sidebar-jira {{ background-color: #FAFBFC; padding: 20px; border-radius: 8px; border: 1px solid #DFE1E6; }}
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA GENERAR PDF
def generar_pdf_con_logo(ticket_data):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image(LOGO_URL, x=10, y=8, w=50)
    except: pdf.text(10, 15, "GRUPO MAGALLAN")
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"ORDEN DE TRABAJO: MAG-{ticket_data['Nro_Ppto']}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Cliente: {ticket_data['Cliente']}")
    pdf.cell(100, 10, txt=f"Entrega: {ticket_data['Fecha_Entrega']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Materiales y Notas Planta:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=str(ticket_data['Materiales_Pendientes']))
    return pdf.output(dest='S').encode('latin-1')

# 3. CONEXIÓN A DATOS
@st.cache_resource
def conectar():
    return gspread.authorize(Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    ))

def get_db(sheet_name):
    try:
        sh = conectar().open("Gestion_Magallan")
        ws = sh.worksheet(sheet_name)
        df = pd.DataFrame(ws.get_all_records())
        return df, ws
    except: return pd.DataFrame(), None

# 4. SISTEMA DE ACCESO
if "authenticated" not in st.session_state:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        u = st.selectbox("Usuario", ["---"] + list(st.secrets["usuarios"].keys()))
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR", use_container_width=True):
            if u != "---" and str(st.secrets["usuarios"][u]).strip() == p.strip():
                st.session_state.update({"authenticated": True, "user": u})
                st.rerun()
else:
    st.sidebar.image(LOGO_URL, use_container_width=True)
    menu = st.sidebar.radio("MENÚ", ["📋 Backlog", "📊 Rendimiento", "🆕 Nuevo Ticket"])
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]; st.rerun()

    # --- A. BACKLOG JIRA ---
    if menu == "📋 Backlog":
        df_p, ws_p = get_db("Proyectos")
        st.title("📋 Control de Planta")
        search = st.text_input("🔍 Buscar presupuesto o cliente...")
        
        if not df_p.empty:
            for _, r in df_p.iterrows():
                if search.lower() in str(r['Nro_Ppto']).lower() or search.lower() in str(r['Cliente']).lower():
                    est = str(r['Estado_Fabricacion']).lower()
                    try:
                        vencido = pd.to_datetime(r['Fecha_Entrega'], dayfirst=True).date() < date.today()
                    except: vencido = False
                    color = "status-terminado" if est in ["terminado", "entregado"] else ("status-atrasado" if vencido else "status-proceso")
                    st.markdown(f"<div class='ticket-card {color}'><b>MAG-{r['Nro_Ppto']}</b> | {r['Cliente']} | {r['Estado_Fabricacion']}</div>", unsafe_allow_html=True)
            
            sel = st.selectbox("Abrir Ticket:", ["---"] + [f"{r['Nro_Ppto']} - {r['Cliente']}" for _, r in df_p.iterrows()])
            if sel != "---":
                nro_id = str(sel.split(" - ")[0])
                tk = df_p[df_p['Nro_Ppto'].astype(str) == nro_id].iloc[0]
                col_main, col_side = st.columns([2, 1])
                
                with col_main:
                    with st.form("edit_f"):
                        st.subheader(f"MAG-{nro_id} - Detalle")
                        f_cli = st.text_input("Cliente", value=tk['Cliente'])
                        f_mon = st.number_input("Monto (ARS)", value=int(tk['Monto_Total_Ars']))
                        f_iva = st.selectbox("IVA", ["sin iva", "iva 21%"], index=0 if "sin" in str(tk['IVA']).lower() else 1)
                        f_mat = st.text_area("Notas Técnicas", value=tk['Materiales_Pendientes'])
                        if st.form_submit_button("Guardar Cambios"):
                            idx = df_p[df_p['Nro_Ppto'].astype(str) == nro_id].index[0] + 2
                            ws_p.update_cell(idx, 2, f_cli); ws_p.update_cell(idx, 6, f_mon)
                            ws_p.update_cell(idx, 8, f_iva); ws_p.update_cell(idx, 10, f_mat)
                            get_db("Historial")[1].append_row([nro_id, datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state['user'], "Editó detalles"])
                            st.rerun()

                with col_side:
                    st.markdown("<div class='sidebar-jira'>", unsafe_allow_html=True)
                    st.download_button("📄 PDF Orden de Trabajo", data=generar_pdf_con_logo(tk), file_name=f"MAG_{nro_id}.pdf")
                    st.markdown("---")
                    new_est = st.selectbox("Estado", ["Esperando", "Preparacion", "Terminado", "Entregado"], index=["Esperando", "Preparacion", "Terminado", "Entregado"].index(tk['Estado_Fabricacion']))
                    if st.button("Actualizar Estado"):
                        idx = df_p[df_p['Nro_Ppto'].astype(str) == nro_id].index[0] + 2
                        ws_p.update_cell(idx, 3, new_est)
                        get_db("Historial")[1].append_row([nro_id, datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state['user'], f"Cambio a {new_est}"])
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # --- B. RENDIMIENTO (NUEVOS GRÁFICOS) ---
    elif menu == "📊 Rendimiento":
        st.title("📊 Rendimiento del Equipo")
        df_h, _ = get_db("Historial")
        if not df_h.empty:
            df_h['Fecha_DT'] = pd.to_datetime(df_h['Fecha_Hora'], dayfirst=True)
            
            # Gráfico 1: Acciones por Usuario
            st.plotly_chart(px.bar(df_h['Usuario'].value_counts().reset_index(), x='Usuario', y='count', color='Usuario', title="Acciones totales por Operador"))
            
            # Gráfico 2: Cortinas Terminadas por Semana (Lo solicitado)
            df_term = df_h[df_h['Detalle'].str.contains("Terminado|Entregado", case=False)].copy()
            if not df_term.empty:
                df_term['Semana'] = df_term['Fecha_DT'].dt.to_period('W').apply(lambda r: r.start_time)
                prod_semanal = df_term.groupby('Semana').size().reset_index(name='Cantidad')
                st.plotly_chart(px.line(prod_semanal, x='Semana', y='Cantidad', title="Cortinas Finalizadas por Semana", markers=True))
            
            st.write("Registro de Auditoría:")
            st.dataframe(df_h.sort_values('Fecha_DT', ascending=False), use_container_width=True)

    # --- C. NUEVO TICKET ---
    elif menu == "🆕 Nuevo Ticket":
        with st.form("alta"):
            st.subheader("Nueva Orden de Trabajo")
            v_n = st.text_input("Número Ppto")
            v_c = st.text_input("Cliente")
            v_m = st.number_input("Monto total", min_value=0)
            v_i = st.selectbox("IVA", ["sin iva", "iva 21%"])
            if st.form_submit_button("Crear Ticket"):
                get_db("Proyectos")[1].append_row([v_n, v_c, "Esperando", date.today().strftime("%d/%m/%Y"), date.today().strftime("%d/%m/%Y"), v_m, 0, v_i, "", ""])
                st.success("Ticket creado correctamente")