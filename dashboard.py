import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="GateGroup Airlines Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Título principal
st.title("✈️ GateGroup Airlines - Dashboard Analítico")
st.markdown("---")

# Función para cargar datos con caché
@st.cache_data
def load_data():
    """Cargar y preparar los datos"""
    df = pd.read_csv(r'Data\Clean\cleaned_data_combined.csv')
    
    # Convertir fechas
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Verificar si existe la columna con el nombre correcto
    if 'departute_local_time' in df.columns:
        df['departute_local_time'] = pd.to_datetime(df['departute_local_time'])
        df['arrival_local_time'] = pd.to_datetime(df['arrival_local_time'])
        # Calcular duración de vuelo
        df['duracion_vuelo_segundos'] = (df['arrival_local_time'] - df['departute_local_time']).dt.total_seconds()
        df['duracion_vuelo_horas'] = df['duracion_vuelo_segundos'] / 3600
    
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
    
    return df

# Cargar datos
with st.spinner('Cargando datos...'):
    df = load_data()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro de fecha
fecha_min = df['fecha'].min().date()
fecha_max = df['fecha'].max().date()

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas:",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtro de warehouse
warehouses = ['Todos'] + sorted(df['warehouse'].unique().tolist())
warehouse_seleccionado = st.sidebar.selectbox("Warehouse:", warehouses)

# Filtro de supercategoría
supercategorias = ['Todas'] + sorted(df['supercategory'].unique().tolist())
supercat_seleccionada = st.sidebar.selectbox("Supercategoría:", supercategorias)

# Filtro de origen
origenes = ['Todos'] + sorted(df['origen'].unique().tolist())
origen_seleccionado = st.sidebar.selectbox("Origen:", origenes)

# Aplicar filtros
df_filtrado = df.copy()
df_filtrado = df_filtrado[
    (df_filtrado['fecha'].dt.date >= fecha_inicio) & 
    (df_filtrado['fecha'].dt.date <= fecha_fin)
]

if warehouse_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['warehouse'] == warehouse_seleccionado]

if supercat_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['supercategory'] == supercat_seleccionada]

if origen_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['origen'] == origen_seleccionado]

# Información de filtros aplicados
st.sidebar.markdown("---")
st.sidebar.metric("Registros filtrados", f"{len(df_filtrado):,}")
st.sidebar.metric("% del total", f"{len(df_filtrado)/len(df)*100:.1f}%")

# KPIs principales
st.header("📊 Indicadores Clave (KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_ventas = df_filtrado['sales'].sum()
    st.metric(
        label="💰 Ventas Totales",
        value=f"${total_ventas:,.0f}",
        delta=f"{total_ventas/len(df_filtrado):.2f} promedio"
    )

with col2:
    total_pasajeros = df_filtrado['passengers'].sum()
    st.metric(
        label="👥 Pasajeros",
        value=f"{total_pasajeros:,}",
        delta=f"{total_pasajeros/len(df_filtrado):.0f} por vuelo"
    )

with col3:
    total_vuelos = df_filtrado['flight_key'].nunique()
    transacciones = len(df_filtrado)
    st.metric(
        label="✈️ Vuelos Únicos",
        value=f"{total_vuelos:,}",
        delta=f"{transacciones:,} transacciones"
    )

with col4:
    ventas_perdidas = df_filtrado['lost_sales'].sum()
    st.metric(
        label="📉 Ventas Perdidas",
        value=f"${ventas_perdidas:,.0f}",
        delta=f"{ventas_perdidas/total_ventas*100:.1f}% del total",
        delta_color="inverse"
    )

with col5:
    if 'duracion_vuelo_horas' in df_filtrado.columns:
        duracion_promedio = df_filtrado['duracion_vuelo_horas'].mean()
        duracion_min = df_filtrado['duracion_vuelo_horas'].min()
        st.metric(
            label="⏱️ Duración Promedio",
            value=f"{duracion_promedio:.1f}h",
            delta=f"Min: {duracion_min:.1f}h"
        )
    else:
        st.metric(
            label="⏱️ Duración Promedio",
            value="N/A",
            delta="No disponible"
        )

st.markdown("---")

# Tabs para organizar el contenido
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Análisis Temporal", 
    "🗺️ Rutas y Geografía", 
    "📦 Productos",
    "💹 Ventas Detalladas",
    "🔍 Análisis Avanzado"
])

# TAB 1: Análisis Temporal
with tab1:
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
            
            st.metric("Duración promedio de vuelo", f"{df_filtrado['duracion_vuelo_horas'].mean():.2f} horas")
            st.metric("Duración mínima", f"{df_filtrado['duracion_vuelo_horas'].min():.2f} horas")
            st.metric("Duración máxima", f"{df_filtrado['duracion_vuelo_horas'].max():.2f} horas")
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
