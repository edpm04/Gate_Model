# ✈️ GateGroup Airlines - Análisis de Datos y Dashboard

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Proyecto de análisis de datos de vuelos y ventas para GateGroup Airlines. Incluye pipeline de limpieza de datos, análisis exploratorio (EDA), modelos de series temporales y dashboard interactivo.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Dataset](#-dataset)
- [Características del Dashboard](#-características-del-dashboard)
- [Análisis Incluidos](#-análisis-incluidos)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Contribuir](#-contribuir)

---

## 🎯 Descripción del Proyecto

Este proyecto analiza datos históricos de vuelos y ventas de GateGroup Airlines para:

- ✅ Limpiar y validar datos de transacciones de vuelos
- ✅ Realizar análisis exploratorio de datos (EDA)
- ✅ Crear modelos predictivos de series temporales
- ✅ Visualizar insights en un dashboard interactivo
- ✅ Identificar patrones de ventas y comportamiento de pasajeros

**Datos analizados:** ~1.3 millones de transacciones (Enero - Agosto 2025)

---

## 📁 Estructura del Proyecto

```
mtyhack/
│
├── Data/
│   ├── Raw/                              # Datos originales (no incluidos en Git)
│   │   ├── result_hack 3.2 REDUCED A.csv
│   │   └── result_hack 3.2 REDUCED b.csv
│   └── Clean/                            # Datos procesados
│       ├── cleaned_data_combined.csv     # Dataset limpio final
│       ├── forecast_ventas_30dias.csv    # Predicciones futuras
│       ├── metricas_modelos.csv          # Resultados de modelos
│       └── cleaning_report.txt           # Reporte de limpieza
│
├── clean_data.py                         # Pipeline de limpieza de datos
├── explore_data.py                       # Script de exploración inicial
├── dashboard.py                          # Dashboard interactivo (Streamlit)
├── eda_analysis.ipynb                    # Notebook de análisis exploratorio
├── time_series_model.ipynb               # Notebook de series temporales
│
├── requirements.txt                      # Dependencias del proyecto
├── .gitignore                           # Archivos ignorados por Git
└── README.md                            # Este archivo
```

---

## 🚀 Instalación

### Prerrequisitos

- Python 3.13 o superior
- Git

### Pasos

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/edpm04/Gate_Model.git
   cd Gate_Model
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   ```

3. **Activar entorno virtual:**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Uso

### 1️⃣ Limpieza de Datos

Ejecutar el pipeline de limpieza de datos:

```bash
python clean_data.py
```

**Pasos del pipeline:**
- ✅ Normalización de nombres de columnas
- ✅ Conversión de tipos de datos
- ✅ Eliminación de duplicados
- ✅ Filtrado de valores inválidos (negativos)
- ✅ Eliminación de valores nulos
- ✅ Validación final y reporte

**Resultado:** `Data/Clean/cleaned_data_combined.csv` (1,293,077 registros limpios)

---

### 2️⃣ Dashboard Interactivo

Iniciar el dashboard:

```bash
streamlit run dashboard.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

### 3️⃣ Análisis Exploratorio (EDA)

Abrir el notebook de análisis:

```bash
jupyter notebook eda_analysis.ipynb
```

**Contenido del notebook:**
- 13 secciones de análisis detallado
- Visualizaciones de distribuciones
- Análisis temporal
- Análisis de rutas y categorías
- Detección de outliers
- Análisis de item codes

---

### 4️⃣ Modelos de Series Temporales

Abrir el notebook de forecasting:

```bash
jupyter notebook time_series_model.ipynb
```

**Modelos implementados:**
- 📊 ARIMA - Modelo autoregresivo
- 📊 SARIMA - ARIMA con estacionalidad
- 📊 Exponential Smoothing (Holt-Winters)

**Salida:** Predicciones para los próximos 30 días

---

## 📊 Dataset

### Información General

- **Registros totales:** 1,293,077 transacciones limpias
- **Período:** Enero - Agosto 2025 (8 meses)
- **Tasa de retención:** 97.06% después de limpieza
- **Vuelos únicos:** ~80,000
- **Item codes únicos:** 171

### Columnas del Dataset

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `flight_key` | object | Identificador único del vuelo |
| `passengers` | int64 | Número de pasajeros |
| `nombre_de_aerolinea` | object | Nombre de la aerolínea |
| `fecha` | datetime64 | Fecha de la transacción |
| `origen` | object | Aeropuerto de origen |
| `destino` | object | Aeropuerto de destino |
| `flight_no` | object | Número de vuelo |
| `departute_local_time` | datetime64 | Hora de salida local |
| `arrival_local_time` | datetime64 | Hora de llegada local |
| `sales` | float64 | Ventas totales ($) |
| `type_transaction` | object | Tipo de transacción |
| `category` | object | Categoría del producto |
| `supercategory` | object | Supercategoría del producto |
| `lost_sales` | float64 | Ventas perdidas ($) |
| `item_code` | int64 | Código del producto |
| `currency` | object | Moneda |
| `warehouse` | object | Almacén |

---

## 🎨 Características del Dashboard

### 📌 KPIs Principales

- 💰 **Ventas Totales** - Con promedio por transacción
- 👥 **Pasajeros** - Con promedio por vuelo
- ✈️ **Vuelos Únicos** - Con total de transacciones
- 📉 **Ventas Perdidas** - Con porcentaje del total
- ⏱️ **Duración Promedio** - De vuelos con duración mínima

### 🔍 Filtros Interactivos

- 📅 Rango de fechas
- 🏪 Warehouse
- 📦 Supercategoría
- 🌍 Aeropuerto de origen

### 📊 Pestañas del Dashboard

#### 1. 📈 Análisis Temporal
- Ventas diarias (gráfico de línea)
- Pasajeros diarios
- Ventas por día de la semana
- Ventas por mes

#### 2. 🗺️ Rutas y Geografía
- Top 15 rutas más frecuentes
- Top 15 rutas por ventas
- Top 10 aeropuertos de origen (gráfico circular)
- Top 10 aeropuertos de destino (gráfico circular)

#### 3. 📦 Productos
- Ventas por supercategoría
- Ventas por warehouse
- Tabla de top 20 items

#### 4. 💹 Ventas Detalladas
- Distribución de ventas (histograma)
- Relación pasajeros vs ventas (scatter plot)
- Mapa de calor: ventas por día y mes

#### 5. 🔍 Análisis Avanzado
- Distribución de duración de vuelos
- Análisis de ventas perdidas
- Resumen detallado por categoría

---

## 🛠️ Tecnologías Utilizadas

### Python Libraries

- **Análisis de Datos:**
  - `pandas` - Manipulación de datos
  - `numpy` - Operaciones numéricas

- **Visualización:**
  - `matplotlib` - Gráficos estáticos
  - `seaborn` - Visualizaciones estadísticas
  - `plotly` - Gráficos interactivos

- **Dashboard:**
  - `streamlit` - Framework de dashboard interactivo

- **Machine Learning:**
  - `scikit-learn` - Métricas y validación
  - `statsmodels` - Modelos de series temporales (ARIMA, SARIMA)

- **Jupyter:**
  - `jupyter` - Notebooks interactivos

---

## 📈 Resultados Clave

### Insights del Análisis

- 📊 **171 item codes únicos** - 52 items (30.4%) generan el 80% de transacciones
- 🏆 **Item más vendido:** 4724 (48,600 transacciones)
- 💰 **Ventas totales:** Análisis detallado por período
- ✈️ **Duración promedio de vuelo:** ~5.1 horas
- 📉 **Ventas perdidas:** Identificadas y cuantificadas

### Calidad de Datos

- ✅ **0 valores nulos** en dataset final
- ✅ **0 duplicados** 
- ✅ **0 valores negativos** en pasajeros y ventas
- ✅ **97.06% de retención** de datos originales

---

## 👥 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Notas

- Los datos crudos (`Data/Raw/`) no están incluidos en el repositorio por su tamaño (>50MB cada archivo)
- El archivo `.gitignore` está configurado para excluir archivos de datos grandes
- El reporte de limpieza (`cleaning_report.txt`) sí está incluido para referencia

---

## 📧 Contacto

**Desarrollador:** EPedraza  
**Email:** emlio.edpm04@gmail.com  
**Repositorio:** [https://github.com/edpm04/Gate_Model](https://github.com/edpm04/Gate_Model)

---

## 🙏 Agradecimientos

- GateGroup Airlines por proporcionar los datos
- Comunidad de Python y Streamlit por las excelentes librerías
- Hackathon organizers

---

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!**

---

*Última actualización: Octubre 2025*
