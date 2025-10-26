import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="GateGroup Airlines Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados mejorados
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }
    .stMetric label {
        color: white !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
        border-bottom: 3px solid #1f77b4;
    }
    h2 {
        padding-top: 20px;
        margin-bottom: 15px;
    }
    .insight-box {
        background-color: rgba(31, 119, 180, 0.1);
        border-left: 5px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: inherit;
    }
    .insight-box h4 {
        color: #1f77b4;
        margin-top: 0;
        font-size: 1.1rem;
    }
    .insight-box p {
        color: inherit;
        margin: 5px 0;
    }
    .alert-box {
        background-color: rgba(255, 193, 7, 0.15);
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: inherit;
    }
    .alert-box h4 {
        color: #ff9800;
        margin-top: 0;
        font-size: 1.1rem;
    }
    .alert-box p {
        color: inherit;
        margin: 5px 0;
    }
    .success-box {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: inherit;
    }
    .success-box h4 {
        color: #28a745;
        margin-top: 0;
        font-size: 1.1rem;
    }
    .success-box p {
        color: inherit;
        margin: 5px 0;
    }
    .success-box strong {
        font-weight: 600;
    }
    .alert-box strong {
        font-weight: 600;
    }
    .insight-box strong {
        font-weight: 600;
    }
    /* Asegurar que el texto sea visible en modo oscuro */
    [data-theme="dark"] .insight-box {
        background-color: rgba(31, 119, 180, 0.2);
    }
    [data-theme="dark"] .alert-box {
        background-color: rgba(255, 193, 7, 0.2);
    }
    [data-theme="dark"] .success-box {
        background-color: rgba(40, 167, 69, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Título principal con contexto de fecha
st.title("✈️ GateGroup Airlines - Executive Dashboard")
col_title1, col_title2 = st.columns([3, 1])
with col_title1:
    st.markdown("### 📊 Business Intelligence & Analytics Platform")
with col_title2:
    st.markdown(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# Función para cargar datos con caché
@st.cache_data
def load_data():
    """Cargar y preparar los datos con métricas de negocio calculadas"""
    df = pd.read_csv(r'Data\Clean\df_maestro_con_temporales.csv')
    
    # Convertir fechas
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Verificar si existe la columna con el nombre correcto
    if 'departute_local_time' in df.columns:
        df['departute_local_time'] = pd.to_datetime(df['departute_local_time'])
        df['arrival_local_time'] = pd.to_datetime(df['arrival_local_time'])
        # Calcular duración de vuelo (usar valor absoluto para evitar negativos por cruces de huso horario)
        df['duracion_vuelo_segundos'] = (df['arrival_local_time'] - df['departute_local_time']).dt.total_seconds()
        df['duracion_vuelo_horas'] = abs(df['duracion_vuelo_segundos'] / 3600)
    
    # Variables temporales
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['mes_nombre'] = df['fecha'].dt.strftime('%B')
    df['semana'] = df['fecha'].dt.isocalendar().week
    df['dia'] = df['fecha'].dt.day
    df['dia_semana'] = df['fecha'].dt.day_name()
    df['dia_semana_num'] = df['fecha'].dt.dayofweek
    
    # Ruta
    df['ruta'] = df['origen'] + ' → ' + df['destino']
    
    # ===== MÉTRICAS DE NEGOCIO CALCULADAS =====
    # Revenue Per Passenger (RPP)
    df['revenue_per_passenger'] = df['sales'] / df['passengers'].replace(0, np.nan)
    
    # Contribution Margin (asumiendo que lost_sales es costo de oportunidad)
    df['contribution_margin'] = df['sales'] - df['lost_sales']
    df['margin_percentage'] = (df['contribution_margin'] / df['sales'].replace(0, np.nan)) * 100
    
    # Clasificación de performance de rutas
    ruta_performance = df.groupby('ruta').agg({
        'sales': 'sum',
        'passengers': 'sum'
    })
    ruta_performance['performance_score'] = (
        (ruta_performance['sales'] / ruta_performance['sales'].max()) * 0.6 +
        (ruta_performance['passengers'] / ruta_performance['passengers'].max()) * 0.4
    )
    df = df.merge(ruta_performance[['performance_score']], left_on='ruta', right_index=True, how='left')
    
    # Clasificación de productos (BCG Matrix simplificada)
    item_sales = df.groupby('item_code')['sales'].sum()
    item_freq = df.groupby('item_code').size()
    
    df['item_sales_rank'] = df['item_code'].map(item_sales.rank(pct=True))
    df['item_freq_rank'] = df['item_code'].map(item_freq.rank(pct=True))
    
    # Clasificación: Star, Cash Cow, Question Mark, Dog
    def classify_product(row):
        if row['item_sales_rank'] >= 0.7 and row['item_freq_rank'] >= 0.7:
            return 'Star ⭐'
        elif row['item_sales_rank'] >= 0.7 and row['item_freq_rank'] < 0.7:
            return 'Cash Cow 💰'
        elif row['item_sales_rank'] < 0.7 and row['item_freq_rank'] >= 0.7:
            return 'Question Mark ❓'
        else:
            return 'Dog 🐕'
    
    df['product_category'] = df.apply(classify_product, axis=1)
    
    return df

# Cargar datos
with st.spinner('Cargando datos...'):
    df = load_data()

# Sidebar - Filtros Mejorados
st.sidebar.image("https://img.icons8.com/fluency/96/000000/airplane-take-off.png", width=80)
st.sidebar.title("🔍 Filtros Avanzados")
st.sidebar.markdown("---")

# Filtro de fecha con presets
st.sidebar.subheader("📅 Período de Análisis")
fecha_min = df['fecha'].min().date()
fecha_max = df['fecha'].max().date()

preset = st.sidebar.selectbox(
    "Selección rápida:",
    ["Personalizado", "Última semana", "Último mes", "Últimos 3 meses", "Todo el período"],
    key="preset_filter"
)

if preset == "Última semana":
    fecha_inicio = fecha_max - timedelta(days=7)
    fecha_fin = fecha_max
elif preset == "Último mes":
    fecha_inicio = fecha_max - timedelta(days=30)
    fecha_fin = fecha_max
elif preset == "Últimos 3 meses":
    fecha_inicio = fecha_max - timedelta(days=90)
    fecha_fin = fecha_max
elif preset == "Todo el período":
    fecha_inicio = fecha_min
    fecha_fin = fecha_max
else:
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Rango personalizado:",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )

st.sidebar.markdown("---")

# Filtros de dimensiones
st.sidebar.subheader("🏢 Dimensiones de Negocio")

# Filtro de aerolínea
aerolineas = ['Todas'] + sorted(df['nombre_de_aerolinea'].unique().tolist())
aerolinea_seleccionada = st.sidebar.selectbox("✈️ Aerolínea:", aerolineas, key="aerolinea_filter")

# Filtro de warehouse
warehouses = ['Todos'] + sorted(df['warehouse'].unique().tolist())
warehouse_seleccionado = st.sidebar.selectbox("🏪 Warehouse:", warehouses, key="warehouse_filter")

# Filtro de supercategoría
supercategorias = ['Todas'] + sorted(df['supercategory'].unique().tolist())
supercat_seleccionada = st.sidebar.selectbox("📦 Supercategoría:", supercategorias, key="supercat_filter")

# Filtro de categoría
categorias = ['Todas'] + sorted(df['category'].unique().tolist())
categoria_seleccionada = st.sidebar.selectbox("📋 Categoría:", categorias, key="categoria_filter")

st.sidebar.markdown("---")

# Filtros geográficos
st.sidebar.subheader("🌍 Geografía")

# Filtro de origen
origenes = ['Todos'] + sorted(df['origen'].unique().tolist())
origen_seleccionado = st.sidebar.selectbox("🛫 Origen:", origenes, key="origen_filter")

# Filtro de destino
destinos = ['Todos'] + sorted(df['destino'].unique().tolist())
destino_seleccionado = st.sidebar.selectbox("🛬 Destino:", destinos, key="destino_filter")

st.sidebar.markdown("---")

# Filtros avanzados
with st.sidebar.expander("⚙️ Filtros Avanzados"):
    # Filtro por tipo de transacción
    tipos_trans = ['Todos'] + sorted(df['type_transaction'].unique().tolist())
    tipo_trans_seleccionado = st.selectbox("Tipo de Transacción:", tipos_trans, key="tipo_trans_filter")
    
    # Filtro por clasificación de producto
    product_cats = ['Todas'] + sorted(df['product_category'].unique().tolist())
    product_cat_seleccionada = st.selectbox("Clasificación de Producto:", product_cats, key="product_cat_filter")

# Aplicar filtros
df_filtrado = df.copy()

# Filtro de fecha
df_filtrado = df_filtrado[
    (df_filtrado['fecha'].dt.date >= fecha_inicio) & 
    (df_filtrado['fecha'].dt.date <= fecha_fin)
]

# Filtros de dimensiones
if aerolinea_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['nombre_de_aerolinea'] == aerolinea_seleccionada]

if warehouse_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['warehouse'] == warehouse_seleccionado]

if supercat_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['supercategory'] == supercat_seleccionada]

if categoria_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['category'] == categoria_seleccionada]

# Filtros geográficos
if origen_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['origen'] == origen_seleccionado]

if destino_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['destino'] == destino_seleccionado]

# Filtros avanzados
if tipo_trans_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['type_transaction'] == tipo_trans_seleccionado]

if product_cat_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['product_category'] == product_cat_seleccionada]

# Información de filtros aplicados con métricas de comparación
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Resumen de Filtros")
st.sidebar.metric("Registros filtrados", f"{len(df_filtrado):,}")
st.sidebar.metric("% del total", f"{len(df_filtrado)/len(df)*100:.1f}%")

# Calcular período anterior para comparación
dias_periodo = (fecha_fin - fecha_inicio).days
fecha_inicio_anterior = fecha_inicio - timedelta(days=dias_periodo)
fecha_fin_anterior = fecha_inicio - timedelta(days=1)

df_periodo_anterior = df[
    (df['fecha'].dt.date >= fecha_inicio_anterior) & 
    (df['fecha'].dt.date <= fecha_fin_anterior)
]

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Resetear Filtros"):
    st.rerun()

# KPIs principales con comparación de período anterior
st.header("📊 Executive Summary - KPIs Principales")

# Calcular KPIs del período actual
total_ventas = df_filtrado['sales'].sum()
total_pasajeros = df_filtrado['passengers'].sum()
total_vuelos = df_filtrado['flight_key'].nunique()
ventas_perdidas = df_filtrado['lost_sales'].sum()
revenue_per_pax = total_ventas / total_pasajeros if total_pasajeros > 0 else 0

# KPIs del período anterior
total_ventas_anterior = df_periodo_anterior['sales'].sum()
total_pasajeros_anterior = df_periodo_anterior['passengers'].sum()
revenue_per_pax_anterior = total_ventas_anterior / total_pasajeros_anterior if total_pasajeros_anterior > 0 else 0

# Calcular variaciones
var_ventas = ((total_ventas - total_ventas_anterior) / total_ventas_anterior * 100) if total_ventas_anterior > 0 else 0
var_pasajeros = ((total_pasajeros - total_pasajeros_anterior) / total_pasajeros_anterior * 100) if total_pasajeros_anterior > 0 else 0
var_rpp = ((revenue_per_pax - revenue_per_pax_anterior) / revenue_per_pax_anterior * 100) if revenue_per_pax_anterior > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label="💰 Revenue Total",
        value=f"${total_ventas:,.0f}",
        delta=f"{var_ventas:+.1f}% vs período anterior"
    )

with col2:
    st.metric(
        label="👥 Total Pasajeros",
        value=f"{total_pasajeros:,}",
        delta=f"{var_pasajeros:+.1f}% vs período anterior"
    )

with col3:
    transacciones = len(df_filtrado)
    st.metric(
        label="✈️ Vuelos Únicos",
        value=f"{total_vuelos:,}",
        delta=f"{transacciones:,} transacciones"
    )

with col4:
    st.metric(
        label="💵 Revenue/Passenger",
        value=f"${revenue_per_pax:.2f}",
        delta=f"{var_rpp:+.1f}% vs período anterior"
    )

with col5:
    pct_perdidas = (ventas_perdidas / total_ventas * 100) if total_ventas > 0 else 0
    st.metric(
        label="📉 Lost Sales",
        value=f"${ventas_perdidas:,.0f}",
        delta=f"{pct_perdidas:.1f}% del revenue",
        delta_color="inverse"
    )

with col6:
    if 'duracion_vuelo_horas' in df_filtrado.columns:
        duracion_promedio = df_filtrado['duracion_vuelo_horas'].mean()
        avg_ticket = total_ventas / transacciones if transacciones > 0 else 0
        st.metric(
            label="🎫 Avg Ticket",
            value=f"${avg_ticket:.2f}",
            delta=f"{duracion_promedio:.1f}h avg flight"
        )
    else:
        avg_ticket = total_ventas / transacciones if transacciones > 0 else 0
        st.metric(
            label="🎫 Avg Ticket",
            value=f"${avg_ticket:.2f}",
            delta=f"{transacciones:,} transactions"
        )

st.markdown("---")

# ===== NUEVA SECCIÓN: INSIGHTS AUTOMÁTICOS =====
st.header("🧠 Insights Automáticos & Alertas")

col_insight1, col_insight2, col_insight3 = st.columns(3)

with col_insight1:
    # Top performing route
    top_ruta = df_filtrado.groupby('ruta')['sales'].sum().sort_values(ascending=False).head(1)
    if len(top_ruta) > 0:
        st.markdown(f"""
        <div class="success-box">
            <h4>🏆 Ruta Top Performance</h4>
            <p><strong>{top_ruta.index[0]}</strong></p>
            <p>Revenue: ${top_ruta.values[0]:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

with col_insight2:
    # Producto estrella
    stars = df_filtrado[df_filtrado['product_category'] == 'Star ⭐']
    if len(stars) > 0:
        top_star = stars.groupby('item_code')['sales'].sum().sort_values(ascending=False).head(1)
        st.markdown(f"""
        <div class="success-box">
            <h4>⭐ Producto Estrella</h4>
            <p><strong>Item Code: {top_star.index[0]}</strong></p>
            <p>Revenue: ${top_star.values[0]:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="insight-box">
            <h4>⭐ Producto Estrella</h4>
            <p>No hay productos clasificados como estrellas en este período</p>
        </div>
        """, unsafe_allow_html=True)

with col_insight3:
    # Alerta de ventas perdidas
    if pct_perdidas > 10:
        st.markdown(f"""
        <div class="alert-box">
            <h4>⚠️ Alerta: Lost Sales</h4>
            <p><strong>{pct_perdidas:.1f}% del revenue perdido</strong></p>
            <p>Acción requerida: Revisar inventario y forecasting</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-box">
            <h4>✅ Lost Sales bajo control</h4>
            <p>{pct_perdidas:.1f}% del revenue</p>
            <p>Dentro del rango aceptable</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Tabs para organizar el contenido - MEJORADOS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Executive Summary",
    "⏱️ Análisis Temporal", 
    "🗺️ Rutas & Performance", 
    "📦 Portfolio de Productos",
    "💹 Análisis Financiero",
    "🔍 Deep Dive Analytics"
])

# TAB 1: EXECUTIVE SUMMARY (NUEVO)
with tab1:
    st.header("📊 Executive Summary Dashboard")
    
    # Sección 1: Performance Overview
    st.subheader("📈 Performance Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge chart de performance
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=revenue_per_pax,
            delta={'reference': revenue_per_pax_anterior, 'relative': False},
            title={'text': "Revenue per Passenger"},
            number={'prefix': "$", 'valueformat': '.4f'},
            gauge={
                'axis': {'range': [0, max(revenue_per_pax * 1.5, 0.01)]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, revenue_per_pax * 0.7], 'color': "#ffcdd2"},
                    {'range': [revenue_per_pax * 0.7, revenue_per_pax * 1.2], 'color': "#c8e6c9"},
                    {'range': [revenue_per_pax * 1.2, revenue_per_pax * 1.5], 'color': "#a5d6a7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': revenue_per_pax_anterior
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Comparación período actual vs anterior
        comparison_data = pd.DataFrame({
            'Métrica': ['Revenue', 'Pasajeros', 'RPP'],
            'Período Actual': [total_ventas, total_pasajeros, revenue_per_pax],
            'Período Anterior': [total_ventas_anterior, total_pasajeros_anterior, revenue_per_pax_anterior],
            'Variación %': [var_ventas, var_pasajeros, var_rpp]
        })
        
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Bar(
            name='Período Actual',
            x=comparison_data['Métrica'],
            y=comparison_data['Período Actual'],
            text=comparison_data['Variación %'].apply(lambda x: f"{x:+.1f}%"),
            textposition='outside',
            marker_color='#1f77b4'
        ))
        fig_comparison.add_trace(go.Bar(
            name='Período Anterior',
            x=comparison_data['Métrica'],
            y=comparison_data['Período Anterior'],
            marker_color='#d3d3d3'
        ))
        fig_comparison.update_layout(
            title='Comparación: Período Actual vs Anterior',
            barmode='group',
            height=300
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Sección 2: Top & Bottom Performers
    st.subheader("🏆 Top & Bottom Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔝 Top 5 Rutas por Revenue**")
        top_routes = df_filtrado.groupby('ruta').agg({
            'sales': 'sum',
            'passengers': 'sum',
            'flight_key': 'nunique'
        }).sort_values('sales', ascending=False).head(5)
        top_routes.columns = ['Revenue', 'Pasajeros', 'Vuelos']
        st.dataframe(
            top_routes.style.format({
                'Revenue': '${:,.0f}',
                'Pasajeros': '{:,.0f}',
                'Vuelos': '{:,.0f}'
            }),
            use_container_width=True
        )
    
    with col2:
        st.markdown("**� Bottom 5 Rutas por Revenue**")
        bottom_routes = df_filtrado.groupby('ruta').agg({
            'sales': 'sum',
            'passengers': 'sum',
            'flight_key': 'nunique'
        }).sort_values('sales', ascending=True).head(5)
        bottom_routes.columns = ['Revenue', 'Pasajeros', 'Vuelos']
        st.dataframe(
            bottom_routes.style.format({
                'Revenue': '${:,.0f}',
                'Pasajeros': '{:,.0f}',
                'Vuelos': '{:,.0f}'
            }),
            use_container_width=True
        )
    
    # Sección 3: Matriz BCG de Productos
    st.subheader("📊 BCG Matrix - Portfolio de Productos")
    
    bcg_summary = df_filtrado.groupby('product_category').agg({
        'sales': 'sum',
        'item_code': 'nunique',
        'flight_key': 'count'
    }).reset_index()
    bcg_summary.columns = ['Categoría', 'Revenue', 'Items Únicos', 'Transacciones']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_bcg = px.scatter(
            bcg_summary,
            x='Items Únicos',
            y='Revenue',
            size='Transacciones',
            color='Categoría',
            title='Matriz BCG - Distribución de Portfolio',
            labels={'Items Únicos': 'Cantidad de Items', 'Revenue': 'Revenue Total ($)'},
            size_max=60
        )
        st.plotly_chart(fig_bcg, use_container_width=True)
    
    with col2:
        st.dataframe(
            bcg_summary.style.format({
                'Revenue': '${:,.0f}',
                'Items Únicos': '{:,.0f}',
                'Transacciones': '{:,.0f}'
            }),
            use_container_width=True
        )

# TAB 2: Análisis Temporal (ACTUALIZADO)
with tab2:
    st.header("📈 Análisis Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ventas por día
        ventas_diarias = df_filtrado.groupby('fecha')['sales'].sum().reset_index()
        fig_ventas_diarias = px.line(
            ventas_diarias,
            x='fecha',
            y='sales',
            title='Ventas Diarias',
            labels={'sales': 'Ventas ($)', 'fecha': 'Fecha'}
        )
        fig_ventas_diarias.update_traces(line_color='#1f77b4', line_width=2)
        fig_ventas_diarias.update_layout(hovermode='x unified')
        st.plotly_chart(fig_ventas_diarias, use_container_width=True)
    
    with col2:
        # Pasajeros por día
        pasajeros_diarios = df_filtrado.groupby('fecha')['passengers'].sum().reset_index()
        fig_pasajeros_diarios = px.line(
            pasajeros_diarios,
            x='fecha',
            y='passengers',
            title='Pasajeros Diarios',
            labels={'passengers': 'Pasajeros', 'fecha': 'Fecha'}
        )
        fig_pasajeros_diarios.update_traces(line_color='#2ca02c', line_width=2)
        fig_pasajeros_diarios.update_layout(hovermode='x unified')
        st.plotly_chart(fig_pasajeros_diarios, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Ventas por día de la semana
        ventas_por_dia_semana = df_filtrado.groupby('dia_semana')['sales'].sum().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])
        
        fig_dia_semana = px.bar(
            x=ventas_por_dia_semana.index,
            y=ventas_por_dia_semana.values,
            title='Ventas por Día de la Semana',
            labels={'x': 'Día', 'y': 'Ventas ($)'},
            color=ventas_por_dia_semana.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_dia_semana, use_container_width=True)
    
    with col4:
        # Ventas por mes
        ventas_por_mes = df_filtrado.groupby('mes')['sales'].sum().reset_index()
        fig_mes = px.bar(
            ventas_por_mes,
            x='mes',
            y='sales',
            title='Ventas por Mes',
            labels={'mes': 'Mes', 'sales': 'Ventas ($)'},
            color='sales',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_mes, use_container_width=True)

# TAB 2: Rutas y Geografía
with tab2:
    st.header("🗺️ Análisis de Rutas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top rutas
        top_rutas = df_filtrado['ruta'].value_counts().head(15).reset_index()
        top_rutas.columns = ['ruta', 'count']
        
        fig_rutas = px.bar(
            top_rutas,
            x='count',
            y='ruta',
            orientation='h',
            title='Top 15 Rutas Más Frecuentes',
            labels={'count': 'Número de Vuelos', 'ruta': 'Ruta'},
            color='count',
            color_continuous_scale='Viridis'
        )
        fig_rutas.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_rutas, use_container_width=True)
    
    with col2:
        # Ventas por ruta
        ventas_por_ruta = df_filtrado.groupby('ruta')['sales'].sum().sort_values(ascending=False).head(15).reset_index()
        
        fig_ventas_ruta = px.bar(
            ventas_por_ruta,
            x='sales',
            y='ruta',
            orientation='h',
            title='Top 15 Rutas por Ventas',
            labels={'sales': 'Ventas ($)', 'ruta': 'Ruta'},
            color='sales',
            color_continuous_scale='RdYlGn'
        )
        fig_ventas_ruta.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_ventas_ruta, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Top orígenes
        top_origenes = df_filtrado['origen'].value_counts().head(10).reset_index()
        top_origenes.columns = ['origen', 'count']
        
        fig_origenes = px.pie(
            top_origenes,
            values='count',
            names='origen',
            title='Top 10 Aeropuertos de Origen',
            hole=0.4
        )
        st.plotly_chart(fig_origenes, use_container_width=True)
    
    with col4:
        # Top destinos
        top_destinos = df_filtrado['destino'].value_counts().head(10).reset_index()
        top_destinos.columns = ['destino', 'count']
        
        fig_destinos = px.pie(
            top_destinos,
            values='count',
            names='destino',
            title='Top 10 Aeropuertos de Destino',
            hole=0.4
        )
        st.plotly_chart(fig_destinos, use_container_width=True)

# TAB 3: Productos
with tab3:
    st.header("📦 Análisis de Productos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ventas por supercategoría
        ventas_supercat = df_filtrado.groupby('supercategory')['sales'].sum().sort_values(ascending=False).reset_index()
        
        fig_supercat = px.bar(
            ventas_supercat,
            x='sales',
            y='supercategory',
            orientation='h',
            title='Ventas por Supercategoría',
            labels={'sales': 'Ventas ($)', 'supercategory': 'Supercategoría'},
            color='sales',
            color_continuous_scale='Purples'
        )
        fig_supercat.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_supercat, use_container_width=True)
    
    with col2:
        # Ventas por warehouse
        ventas_warehouse = df_filtrado.groupby('warehouse')['sales'].sum().sort_values(ascending=False).reset_index()
        
        fig_warehouse = px.bar(
            ventas_warehouse,
            x='warehouse',
            y='sales',
            title='Ventas por Warehouse',
            labels={'sales': 'Ventas ($)', 'warehouse': 'Warehouse'},
            color='sales',
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig_warehouse, use_container_width=True)
    
    # Top items
    st.subheader("🏆 Top Items por Ventas")
    top_items = df_filtrado.groupby('item_code').agg({
        'sales': 'sum',
        'passengers': 'sum',
        'flight_key': 'count'
    }).sort_values('sales', ascending=False).head(20)
    top_items.columns = ['Ventas Totales', 'Pasajeros', 'Transacciones']
    top_items.index.name = 'Item Code'
    
    st.dataframe(
        top_items.style.format({
            'Ventas Totales': '${:,.2f}',
            'Pasajeros': '{:,.0f}',
            'Transacciones': '{:,.0f}'
        }),
        use_container_width=True
    )

# TAB 4: Ventas Detalladas
with tab4:
    st.header("💹 Análisis Detallado de Ventas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de ventas
        fig_dist_ventas = px.histogram(
            df_filtrado,
            x='sales',
            nbins=50,
            title='Distribución de Ventas',
            labels={'sales': 'Ventas ($)', 'count': 'Frecuencia'}
        )
        st.plotly_chart(fig_dist_ventas, use_container_width=True)
    
    with col2:
        # Relación pasajeros vs ventas
        sample_data = df_filtrado.sample(n=min(5000, len(df_filtrado)))
        fig_scatter = px.scatter(
            sample_data,
            x='passengers',
            y='sales',
            title='Relación: Pasajeros vs Ventas',
            labels={'passengers': 'Pasajeros', 'sales': 'Ventas ($)'},
            opacity=0.6,
            color='sales',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Heatmap de ventas
    st.subheader("🔥 Mapa de Calor: Ventas por Día y Mes")
    heatmap_data = df_filtrado.groupby(['mes', 'dia'])['sales'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='dia', columns='mes', values='sales')
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Mes", y="Día del Mes", color="Ventas ($)"),
        aspect="auto",
        color_continuous_scale='YlOrRd'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# TAB 5: Análisis Avanzado
with tab5:
    st.header("🔍 Análisis Avanzado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análisis de duración de vuelo (solo si existe la columna)
        if 'duracion_vuelo_horas' in df_filtrado.columns:
            fig_duracion = px.histogram(
                df_filtrado,
                x='duracion_vuelo_horas',
                nbins=50,
                title='Distribución de Duración de Vuelos',
                labels={'duracion_vuelo_horas': 'Duración (horas)', 'count': 'Frecuencia'}
            )
            st.plotly_chart(fig_duracion, use_container_width=True)
            
            # Asegurar que los valores mostrados sean positivos
            duracion_promedio = abs(df_filtrado['duracion_vuelo_horas'].mean())
            duracion_minima = abs(df_filtrado['duracion_vuelo_horas'].min())
            duracion_maxima = abs(df_filtrado['duracion_vuelo_horas'].max())
            
            st.metric("Duración promedio de vuelo", f"{duracion_promedio:.2f} horas")
            st.metric("Duración mínima", f"{duracion_minima:.2f} horas")
            st.metric("Duración máxima", f"{duracion_maxima:.2f} horas")
        else:
            st.info("📊 Análisis de duración de vuelo no disponible - columnas de tiempo no encontradas")
    
    with col2:
        # Análisis de ventas perdidas
        fig_lost_sales = px.box(
            df_filtrado,
            y='lost_sales',
            title='Distribución de Ventas Perdidas',
            labels={'lost_sales': 'Ventas Perdidas ($)'}
        )
        st.plotly_chart(fig_lost_sales, use_container_width=True)
        
        pct_perdidas = (df_filtrado['lost_sales'].sum() / df_filtrado['sales'].sum() * 100)
        st.metric("% Ventas Perdidas", f"{pct_perdidas:.2f}%")
        st.metric("Total Ventas Perdidas", f"${df_filtrado['lost_sales'].sum():,.0f}")
    
    # Tabla de resumen por categoría
    st.subheader("📊 Resumen por Categoría")
    resumen_categoria = df_filtrado.groupby('category').agg({
        'sales': ['sum', 'mean', 'count'],
        'passengers': 'sum',
        'lost_sales': 'sum'
    }).round(2)
    resumen_categoria.columns = ['Ventas Totales', 'Venta Promedio', 'Transacciones', 'Pasajeros', 'Ventas Perdidas']
    resumen_categoria = resumen_categoria.sort_values('Ventas Totales', ascending=False)
    
    st.dataframe(
        resumen_categoria.style.format({
            'Ventas Totales': '${:,.2f}',
            'Venta Promedio': '${:,.2f}',
            'Transacciones': '{:,.0f}',
            'Pasajeros': '{:,.0f}',
            'Ventas Perdidas': '${:,.2f}'
        }),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>📊 Dashboard desarrollado para GateGroup Airlines | Datos actualizados: {} </p>
        <p>Total de registros en el sistema: {:,}</p>
    </div>
""".format(df['fecha'].max().strftime('%Y-%m-%d'), len(df)), unsafe_allow_html=True)
