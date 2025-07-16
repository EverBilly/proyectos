import streamlit as st
import plotly.express as px
import pandas as pd
from analysis import load_data, calculate_metrics, prepare_analysis_data, generate_report_data
import base64
from io import BytesIO

# Configuración de página
st.set_page_config(layout="wide", page_title="Análisis de Trading Pro")

# Título y descripción
st.title("📊 Dashboard Profesional de Trading")
st.markdown("""
**Herramienta completa para análisis de operaciones** con filtros interactivos, drawdown, heatmap y exportación de reportes.
""")

# --- Carga de datos ---
try:
    df = load_data("/data/backtesting_operaciones.xlsx")
    st.success(f"✅ Datos cargados correctamente - {len(df)} operaciones")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.stop()

# --- Filtros Interactivos ---
st.sidebar.header("🔍 Filtros")

# Filtro por divisa
if 'DIVISA' in df.columns:
    divisas = ['Todas'] + sorted(df['DIVISA'].unique().tolist())
    selected_divisa = st.sidebar.selectbox("Divisa", divisas)
    if selected_divisa != 'Todas':
        df = df[df['DIVISA'] == selected_divisa]

# Filtro por resultado
resultados = ['Todos', 'Ganadoras', 'Perdedoras']
selected_resultado = st.sidebar.selectbox("Resultado", resultados)
if selected_resultado == 'Ganadoras':
    df = df[df['RESULTADO $'] > 0]
elif selected_resultado == 'Perdedoras':
    df = df[df['RESULTADO $'] < 0]

# Filtro por fecha (si existe)
if 'FECHA' in df.columns:
    min_date = df['FECHA'].min().date()
    max_date = df['FECHA'].max().date()
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        df = df[(df['FECHA'].dt.date >= date_range[0]) & (df['FECHA'].dt.date <= date_range[1])]

# --- Análisis y visualizaciones ---
analysis_data = prepare_analysis_data(df)
metrics = calculate_metrics(df)
metrics['max_drawdown'] = analysis_data['cumulative_data']['DRAWDOWN'].min() if analysis_data else 0

# Métricas clave
st.header("📈 Métricas Clave")
cols = st.columns(4)
cols[0].metric("Operaciones", metrics['total_ops'])
cols[1].metric("Win Rate", f"{metrics['win_rate']:.2%}")
cols[2].metric("Profit Total", f"${metrics['total_profit']:,.2f}")
cols[3].metric("Max Drawdown", f"${-metrics['max_drawdown']:,.2f}")

cols = st.columns(4)
cols[0].metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
cols[1].metric("Avg Ganancia", f"${metrics['avg_win']:,.2f}")
cols[2].metric("Avg Pérdida", f"${metrics['avg_loss']:,.2f}")
cols[3].metric("Ratio TP/SL", f"{metrics['avg_tp']/metrics['avg_sl']:.2f}" if metrics['avg_sl'] != 0 else "N/A")

# Gráficos principales
tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribución", "🚀 Acumulado", "🔥 Heatmap", "📉 Drawdown"])

with tab1:
    fig_dist = px.histogram(
        analysis_data['distribution_data'],
        x='RESULTADO $',
        color='RESULTADO_TIPO',
        nbins=30,
        title='Distribución de Ganacias y Pérdidas',
        color_discrete_map={'Ganancia': '#2ecc71', 'Pérdida': '#e74c3c'},
        labels={'RESULTADO $': 'Monto ($)', 'count': 'Operaciones'}
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    fig_cum = px.line(
        analysis_data['cumulative_data'],
        x='OPERACIÓN',
        y='PROFIT_ACUMULADO',
        title='Evolución del Capital',
        labels={'OPERACIÓN': 'N° Operación', 'PROFIT_ACUMULADO': 'Profit Acumulado ($)'}
    )
    st.plotly_chart(fig_cum, use_container_width=True)

with tab3:
    if analysis_data['heatmap_data'] is not None:
        fig_heat = px.imshow(
            analysis_data['heatmap_data'],
            labels=dict(x="Hora del día", y="Día de semana", color="Profit"),
            color_continuous_scale='RdYlGn',
            title='Profit por Día y Hora'
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("No se encontraron datos de fecha para generar el heatmap")

with tab4:
    fig_dd = px.area(
        analysis_data['cumulative_data'],
        x='OPERACIÓN',
        y='DRAWDOWN',
        title='Drawdown Histórico',
        labels={'OPERACIÓN': 'N° Operación', 'DRAWDOWN': 'Drawdown ($)'}
    )
    fig_dd.add_hline(y=0, line_color='red')
    st.plotly_chart(fig_dd, use_container_width=True)

# --- Exportación de Reportes ---
st.sidebar.header("📤 Exportar Reporte")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos Completos')
    return output.getvalue()

if st.sidebar.button("Generar Reporte PDF"):
    report_data = generate_report_data(df, metrics)
    # Aquí iría la generación real del PDF (usando ReportLab u otra librería)
    st.sidebar.success("Reporte generado (simulación)")

if st.sidebar.button("Exportar a Excel"):
    excel_data = to_excel(df)
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="reporte_trading.xlsx">Descargar Excel</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# --- Vista de datos ---
with st.expander("🔍 Ver datos completos"):
    st.dataframe(df)

# --- Instrucciones ---
st.sidebar.header("ℹ️ Instrucciones")
st.sidebar.info("""
1. Usa los filtros para analizar subconjuntos de datos
2. Explora las diferentes pestañas de visualización
3. Exporta reportes en PDF o Excel
""")