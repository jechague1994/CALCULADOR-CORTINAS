import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from fpdf import FPDF
import plotly.express as px

# URL del logo oficial
LOGO_URL = "https://r.jina.ai/i/0586f37648354c4193568c07d3967484"

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Magallan | Gestión, Finanzas y Logística", layout="wide")

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
    .status-pagado {{ border-left-color: #6554C0 !important; background-color: #EAE6FF; }}
    .sidebar-jira {{ background-color: #FAFBFC; padding: 20px; border-radius: 8px; border: 1px solid #DFE1E6; }}
    .saldo-alerta {{ color: #BF2600; font-weight: bold; font-size: 1.2em; }}
    .pago-total {{ color: #403294; font-weight: bold; font-size: 1.2em; }}
    </style>
    """, unsafe_allow_html=True)

# 2. GENERADOR DE PDF (Con Logo, Saldos y Ubicación)
def generar_pdf_magallan(tk):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image(LOGO_URL, x=10, y=8, w=50)
    except: pdf.text(10, 15, "GRUPO MAGALLAN")
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"ORDEN DE TRABAJO: MAG-{tk['Nro_Ppto']}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(100, 8, txt=f"Cliente: {tk['Cliente']}")
    pdf.cell(100, 8, txt=f"Ubicación: {tk.get('Ubicacion', 'No especificada')}", ln=True)
    pdf.cell(100, 8, txt=f"Entrega Estimada: {tk['Fecha_Entrega']}", ln=True)
    
    monto = int(tk['Monto_Total_Ars'])
    pago = int(tk.get('Pagado_Ars', 0)) if str(tk.get('Pagado_Ars')).isdigit() else 0
    saldo = monto - pago
    
    pdf.cell(100, 8, txt=f"Monto Total: ${monto}")
    pdf.cell(100, 8, txt=f"Saldo Pendiente: ${saldo}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Especificaciones Técnicas:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=str(tk['Materiales_Pendientes']))
    return pdf.output(dest='S').encode('latin-1')

# 3. CONEXIÓN DATA
@st.cache_resource
def conectar_db():
    return gspread.authorize(Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    ))

def cargar_datos(sheet_name):
    try:
        sh = conectar_db().open("Gestion_Magallan")
        ws = sh.worksheet(sheet_name)
        return pd.DataFrame(ws.get_all_records()), ws
    except: return pd.DataFrame(), None

# 4. APLICACIÓN
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
    opcion = st.sidebar.radio("MENÚ", ["📋 Backlog", "📊 Rendimiento", "🆕 Nueva Obra"])
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]; st.rerun()

    if opcion == "📋 Backlog":
        df_p, ws_p = cargar_datos("Proyectos")
        st.title("📋 Control de Obras")
        busqueda = st.text_input("🔍 Buscar Cliente o Localidad...")
        
        if not df_p.empty:
            for _, r in df_p.iterrows():
                if busqueda.lower() in str(r['Cliente']).lower() or busqueda.lower() in str(r.get('Ubicacion', '')).lower():
                    monto = int(r['Monto_Total_Ars'])
                    pago = int(r.get('Pagado_Ars', 0)) if str(r.get('Pagado_Ars')).isdigit() else 0
                    saldo = monto - pago
                    
                    try: vencido = pd.to_datetime(r['Fecha_Entrega'], dayfirst=True).date() < date.today()
                    except: vencido = False
                    
                    clase = "status-pagado" if saldo <= 0 else ("status-terminado" if str(r['Estado_Fabricacion']).lower() in ["terminado", "entregado"] else ("status-atrasado" if vencido else "status-proceso"))
                    
                    st.markdown(f"<div class='ticket-card {clase}'><b>MAG-{r['Nro_Ppto']}</b> | {r['Cliente']} | {r.get('Ubicacion', 'S/D')} | Saldo: ${saldo}</div>", unsafe_allow_html=True)
            
            sel_ppto = st.selectbox("Seleccione para Editar / PDF:", ["---"] + [f"{r['Nro_Ppto']} - {r['Cliente']}" for _, r in df_p.iterrows()])
            if sel_ppto != "---":
                id_sel = str(sel_ppto.split(" - ")[0])
                tk_sel = df_p[df_p['Nro_Ppto'].astype(str) == id_sel].iloc[0]
                
                c_izq, c_der = st.columns([2, 1])
                with c_izq:
                    with st.form("edit_mag"):
                        f_nom = st.text_input("Cliente", value=tk_sel['Cliente'])
                        f_ubi = st.text_input("Ubicación / Localidad", value=tk_sel.get('Ubicacion', ''))
                        c1, c2 = st.columns(2)
                        f_tot = c1.number_input("Monto Total", value=int(tk_sel['Monto_Total_Ars']))
                        f_pag = c2.number_input("Monto Pagado", value=int(tk_sel.get('Pagado_Ars', 0) if str(tk_sel.get('Pagado_Ars')).isdigit() else 0))
                        f_iva = st.selectbox("IVA", ["sin iva", "iva 21%"], index=0 if "sin" in str(tk_sel['IVA']).lower() else 1)
                        f_mat = st.text_area("Notas Técnicas", value=tk_sel['Materiales_Pendientes'])
                        
                        if st.form_submit_button("GUARDAR CAMBIOS"):
                            idx = df_p[df_p['Nro_Ppto'].astype(str) == id_sel].index[0] + 2
                            ws_p.update_cell(idx, 2, f_nom); ws_p.update_cell(idx, 6, f_tot)
                            ws_p.update_cell(idx, 7, f_pag); ws_p.update_cell(idx, 8, f_iva)
                            ws_p.update_cell(idx, 10, f_mat); ws_p.update_cell(idx, 11, f_ubi)
                            cargar_datos("Historial")[1].append_row([id_sel, datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state['user'], "Edición Logística/Finanzas"])
                            st.rerun()

                with c_der:
                    st.markdown("<div class='sidebar-jira'>", unsafe_allow_html=True)
                    actual_saldo = f_tot - f_pag
                    if actual_saldo <= 0: st.markdown("<p class='pago-total'>✅ SALDO CUBIERTO</p>", unsafe_allow_html=True)
                    else: st.markdown(f"<p class='saldo-alerta'>PENDIENTE: ${actual_saldo}</p>", unsafe_allow_html=True)
                    
                    st.download_button("📄 DESCARGAR PDF", data=generar_pdf_magallan(tk_sel), file_name=f"Orden_MAG_{id_sel}.pdf")
                    st.markdown("---")
                    nuevo_est = st.selectbox("Estado", ["Esperando", "Preparacion", "Terminado", "Entregado"], index=["Esperando", "Preparacion", "Terminado", "Entregado"].index(tk_sel['Estado_Fabricacion']))
                    if st.button("ACTUALIZAR ESTADO"):
                        idx = df_p[df_p['Nro_Ppto'].astype(str) == id_sel].index[0] + 2
                        ws_p.update_cell(idx, 3, nuevo_est)
                        cargar_datos("Historial")[1].append_row([id_sel, datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state['user'], f"Estado: {nuevo_est}"])
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    elif opcion == "📊 Rendimiento":
        st.title("📊 Rendimiento")
        df_h, _ = cargar_datos("Historial")
        if not df_h.empty:
            df_h['f'] = pd.to_datetime(df_h['Fecha_Hora'], dayfirst=True, errors='coerce')
            df_h = df_h.dropna(subset=['f'])
            st.plotly_chart(px.bar(df_h['Usuario'].value_counts().reset_index(), x='Usuario', y='count', color='Usuario', title="Acciones por Operador"))
            df_h['Semana'] = df_h['f'].dt.to_period('W').apply(lambda r: r.start_time)
            st.plotly_chart(px.line(df_h.groupby('Semana').size().reset_index(name='T'), x='Semana', y='T', title="Actividad Semanal", markers=True))

    elif opcion == "🆕 Nueva Obra":
        with st.form("alta"):
            st.subheader("Cargar Nuevo Presupuesto")
            v_n = st.text_input("Número")
            v_c = st.text_input("Cliente")
            v_u = st.text_input("Ubicación")
            v_m = st.number_input("Monto Total", min_value=0)
            v_p = st.number_input("Seña", min_value=0)
            v_i = st.selectbox("IVA", ["sin iva", "iva 21%"])
            if st.form_submit_button("CREAR"):
                cargar_datos("Proyectos")[1].append_row([v_n, v_c, "Esperando", date.today().strftime("%d/%m/%Y"), date.today().strftime("%d/%m/%Y"), v_m, v_p, v_i, "", "", v_u])
                st.success("Creado")