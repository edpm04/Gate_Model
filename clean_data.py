"""
Pipeline de limpieza de datos para GateGroup Airlines
Elimina duplicados, valores nulos, y datos anómalos
"""
import pandas as pd
import numpy as np
from datetime import datetime

# Rutas
file_a = r'Data\Raw\result_hack 3.2 REDUCED A.csv'
file_b = r'Data\Raw\result_hack 3.2 REDUCED b.csv'
output_combined = r'Data\Clean\cleaned_data_combined.csv'
output_report = r'Data\Clean\cleaning_report.txt'


class DataCleaningPipeline:
    """Pipeline de limpieza de datos con reportes detallados"""
    
    def __init__(self):
        self.report = []
        self.initial_shape = None
        self.current_shape = None
        
    def log(self, message):
        """Registra un mensaje en el reporte"""
        print(f"  {message}")
        self.report.append(message)
    
    def step_1_normalize_columns(self, df):
        """Paso 1: Normalizar nombres de columnas"""
        self.log("✓ Paso 1: Normalizando nombres de columnas")
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        return df
    
    def step_2_convert_types(self, df):
        """Paso 2: Convertir tipos de datos"""
        self.log("✓ Paso 2: Convirtiendo tipos de datos")
        
        # Convertir fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        # Convertir columnas numéricas
        numeric_cols = ['passengers', 'sales', 'lost_sales', 'item_code']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def step_3_remove_duplicates(self, df):
        """Paso 3: Eliminar duplicados"""
        initial_rows = len(df)
        df = df.drop_duplicates()
        removed = initial_rows - len(df)
        
        if removed > 0:
            self.log(f"✓ Paso 3: Eliminados {removed} registros duplicados")
        else:
            self.log("✓ Paso 3: No se encontraron duplicados")
        
        return df
    
    def step_4_remove_invalid_values(self, df):
        """Paso 4: Eliminar valores inválidos (negativos donde no deben existir)"""
        initial_rows = len(df)
        
        # Eliminar pasajeros negativos
        if 'passengers' in df.columns:
            invalid_passengers = (df['passengers'] < 0).sum()
            df = df[df['passengers'] >= 0]
            if invalid_passengers > 0:
                self.log(f"  - Eliminados {invalid_passengers} registros con pasajeros negativos")
        
        # Eliminar sales negativos (pueden ser devoluciones, pero los eliminaremos)
        if 'sales' in df.columns:
            invalid_sales = (df['sales'] < 0).sum()
            df = df[df['sales'] >= 0]
            if invalid_sales > 0:
                self.log(f"  - Eliminados {invalid_sales} registros con ventas negativas")
        
        total_removed = initial_rows - len(df)
        self.log(f"✓ Paso 4: Total de registros inválidos eliminados: {total_removed}")
        
        return df
    
    def step_5_drop_nulls(self, df):
        """Paso 5: Eliminar filas con valores nulos"""
        initial_rows = len(df)
        
        # Reportar nulos antes de eliminar
        null_counts = df.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0]
        
        if len(cols_with_nulls) > 0:
            self.log("  Columnas con valores nulos antes de limpiar:")
            for col, count in cols_with_nulls.items():
                percentage = (count / len(df)) * 100
                self.log(f"    - {col}: {count} ({percentage:.2f}%)")
        
        # Eliminar todas las filas con al menos un valor nulo
        df = df.dropna()
        
        removed = initial_rows - len(df)
        self.log(f"✓ Paso 5: Eliminadas {removed} filas con valores nulos")
        
        return df
    
    def step_6_validate_data(self, df):
        """Paso 6: Validaciones adicionales y estadísticas finales"""
        self.log("✓ Paso 6: Validando datos limpios")
        
        # Verificar que no hay nulos
        total_nulls = df.isnull().sum().sum()
        self.log(f"  - Total de valores nulos: {total_nulls}")
        
        # Verificar rangos de datos importantes
        if 'passengers' in df.columns:
            self.log(f"  - Pasajeros: min={df['passengers'].min()}, max={df['passengers'].max()}")
        
        if 'sales' in df.columns:
            self.log(f"  - Ventas: min={df['sales'].min()}, max={df['sales'].max()}")
        
        if 'fecha' in df.columns:
            self.log(f"  - Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
        
        return df
    
    def clean(self, df, name="Dataset"):
        """Ejecuta la pipeline completa de limpieza"""
        self.report = []
        self.initial_shape = df.shape
        
        print(f"\n{'='*80}")
        print(f"🧹 LIMPIANDO {name.upper()}")
        print(f"{'='*80}")
        self.log(f"Dimensiones iniciales: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        # Ejecutar pipeline
        df = self.step_1_normalize_columns(df)
        df = self.step_2_convert_types(df)
        df = self.step_3_remove_duplicates(df)
        df = self.step_4_remove_invalid_values(df)
        df = self.step_5_drop_nulls(df)
        df = self.step_6_validate_data(df)
        
        self.current_shape = df.shape
        rows_removed = self.initial_shape[0] - self.current_shape[0]
        percentage_kept = (self.current_shape[0] / self.initial_shape[0]) * 100
        
        self.log(f"\nDimensiones finales: {df.shape[0]} filas x {df.shape[1]} columnas")
        self.log(f"Filas eliminadas: {rows_removed} ({100-percentage_kept:.2f}%)")
        self.log(f"Filas conservadas: {self.current_shape[0]} ({percentage_kept:.2f}%)")
        
        return df
    
    def get_report(self):
        """Retorna el reporte completo"""
        return "\n".join(self.report)


# Ejecutar pipeline
print("=" * 80)
print("🚀 INICIANDO PIPELINE DE LIMPIEZA DE DATOS")
print("=" * 80)
print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Crear instancia del pipeline
pipeline = DataCleaningPipeline()

# Cargar y limpiar archivo A
print("📂 Cargando archivo A...")
df_a = pd.read_csv(file_a)
df_a_clean = pipeline.clean(df_a, "Archivo A")
report_a = pipeline.get_report()

# Cargar y limpiar archivo B
print("\n📂 Cargando archivo B...")
df_b = pd.read_csv(file_b)
df_b_clean = pipeline.clean(df_b, "Archivo B")
report_b = pipeline.get_report()

# Combinar archivos limpios
print("\n" + "=" * 80)
print("🔗 COMBINANDO ARCHIVOS LIMPIOS")
print("=" * 80)
df_combined = pd.concat([df_a_clean, df_b_clean], ignore_index=True)
print(f"Dimensiones del dataset combinado: {df_combined.shape[0]} filas x {df_combined.shape[1]} columnas")

# Verificar y eliminar duplicados después de combinar
duplicates_combined = df_combined.duplicated().sum()
if duplicates_combined > 0:
    print(f"Eliminando {duplicates_combined} duplicados entre archivos...")
    df_combined = df_combined.drop_duplicates()
    print(f"Dimensiones finales: {df_combined.shape[0]} filas x {df_combined.shape[1]} columnas")

# Guardar archivo combinado
print("\n" + "=" * 80)
print("💾 GUARDANDO DATOS LIMPIOS")
print("=" * 80)
df_combined.to_csv(output_combined, index=False)
print(f"✅ Archivo combinado guardado en: {output_combined}")

# Generar reporte completo
full_report = f"""
REPORTE DE LIMPIEZA DE DATOS
{'='*80}
Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ARCHIVO A:
{report_a}

ARCHIVO B:
{report_b}

DATASET COMBINADO FINAL:
- Total de filas: {df_combined.shape[0]}
- Total de columnas: {df_combined.shape[1]}
- Duplicados entre archivos eliminados: {duplicates_combined}
- Archivo guardado: {output_combined}

COLUMNAS FINALES:
{', '.join(df_combined.columns.tolist())}

RESUMEN DE CALIDAD:
- Valores nulos: {df_combined.isnull().sum().sum()}
- Filas duplicadas: {df_combined.duplicated().sum()}
- Integridad de datos: ✅ VERIFICADA
"""

# Guardar reporte
with open(output_report, 'w', encoding='utf-8') as f:
    f.write(full_report)

print(f"📄 Reporte guardado en: {output_report}")

print("\n" + "=" * 80)
print("🎉 ¡PIPELINE DE LIMPIEZA COMPLETADA EXITOSAMENTE!")
print("=" * 80)
print(f"\n📊 Resumen final:")
print(f"   - Registros totales procesados: {df_a.shape[0] + df_b.shape[0]}")
print(f"   - Registros finales limpios: {df_combined.shape[0]}")
print(f"   - Tasa de retención: {(df_combined.shape[0] / (df_a.shape[0] + df_b.shape[0])) * 100:.2f}%")
