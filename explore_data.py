"""
Script para explorar los datos antes de limpiarlos
Optimizado para archivos grandes
"""
import pandas as pd
import numpy as np

# Rutas de los archivos
file_a = r'Data\Raw\result_hack 3.2 REDUCED A.csv'
file_b = r'Data\Raw\result_hack 3.2 REDUCED b.csv'

print("=" * 80)
print("EXPLORANDO ARCHIVO A")
print("=" * 80)

# Leer el archivo A (solo las primeras 10000 filas para exploración rápida)
print("Cargando archivo A (muestra de 10,000 filas)...")
df_a = pd.read_csv(file_a, nrows=10000)

print(f"\n📊 Dimensiones: {df_a.shape[0]} filas x {df_a.shape[1]} columnas")
print(f"\n📋 Columnas:")
print(df_a.columns.tolist())

print(f"\n🔍 Información general:")
print(df_a.info())

print(f"\n📈 Primeras filas:")
print(df_a.head())

print(f"\n❌ Valores nulos por columna:")
print(df_a.isnull().sum())

print(f"\n📊 Porcentaje de valores nulos:")
print((df_a.isnull().sum() / len(df_a) * 100).round(2))

print(f"\n🔢 Duplicados: {df_a.duplicated().sum()}")

print(f"\n📊 Estadísticas descriptivas (columnas numéricas):")
print(df_a.describe())

print("\n" + "=" * 80)
print("EXPLORANDO ARCHIVO B")
print("=" * 80)

# Leer el archivo B (solo las primeras 10000 filas para exploración rápida)
print("Cargando archivo B (muestra de 10,000 filas)...")
df_b = pd.read_csv(file_b, nrows=10000)

print(f"\n📊 Dimensiones: {df_b.shape[0]} filas x {df_b.shape[1]} columnas")
print(f"\n📋 Columnas:")
print(df_b.columns.tolist())

print(f"\n🔍 Información general:")
print(df_b.info())

print(f"\n📈 Primeras filas:")
print(df_b.head())

print(f"\n❌ Valores nulos por columna:")
print(df_b.isnull().sum())

print(f"\n📊 Porcentaje de valores nulos:")
print((df_b.isnull().sum() / len(df_b) * 100).round(2))

print(f"\n🔢 Duplicados: {df_b.duplicated().sum()}")

print(f"\n📊 Estadísticas descriptivas (columnas numéricas):")
print(df_b.describe())

print("\n" + "=" * 80)
print("COMPARACIÓN ENTRE ARCHIVOS")
print("=" * 80)

print(f"\n¿Tienen las mismas columnas? {set(df_a.columns) == set(df_b.columns)}")
if set(df_a.columns) != set(df_b.columns):
    print(f"Columnas solo en A: {set(df_a.columns) - set(df_b.columns)}")
    print(f"Columnas solo en B: {set(df_b.columns) - set(df_a.columns)}")
