import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ruta del archivo de entrada
input_file_path = 'report.txt'  # Cambia esta ruta a la ubicación de tu archivo de texto

# eer el archivo TXT delimitado por múltiples espacios
try:
    #Intentar leer con delimitador explícito de múltiples espacios
    data = pd.read_csv(input_file_path, sep='\s{2,}', engine='python', header=0)
#Error handling
except Exception as e:
    raise ValueError(f"Error al leer el archivo TXT: {e}")

# Identificar columnas de la ISS y los objetos
iss_columns = ['ISS.EarthMJ2000Eq.X', 'ISS.EarthMJ2000Eq.Y', 'ISS.EarthMJ2000Eq.Z']
objects_columns = [
    col for col in data.columns if 'EarthMJ2000Eq' in col and not col.startswith('ISS')
]

# Verificar que las columnas necesarias existan
if not all(col in data.columns for col in iss_columns):
    raise ValueError("No se encontraron todas las columnas de la ISS en los datos.")
if len(objects_columns) % 3 != 0:
    raise ValueError("El número de columnas de objetos no es múltiplo de 3. Verifique el formato del archivo.")

# Asegurarse de que las columnas sean numéricas
data[iss_columns + objects_columns] = data[iss_columns + objects_columns].apply(pd.to_numeric, errors='coerce')

# Verificar si hay valores no numéricos
data.dropna(subset=iss_columns + objects_columns, inplace=True)
if data.empty:
    raise ValueError("El archivo contiene solo datos no numéricos o faltantes tras la conversión.")

# Separar las coordenadas de la ISS
iss_coords = data[iss_columns].values

# Calcular la distancia relativa
distances = pd.DataFrame()
for i in range(0, len(objects_columns), 3):
    obj_name = objects_columns[i].split('.')[0]  # Nombre del objeto (por ejemplo, "debris_1")
    obj_coords = data[objects_columns[i:i+3]].values

    # Calcular la distancia euclidiana
    distance = np.sqrt(np.sum((obj_coords - iss_coords)**2, axis=1))

    # Agregar al DataFrame de distancias
    distances[obj_name] = distance

# Verificar los datos calculados
print("Primeras filas de las distancias calculadas:")
print(distances.head())

# Graficar las distancias
plt.figure(figsize=(12, 6))
for column in distances.columns:
    plt.plot(distances.index, distances[column], label=column)

plt.title('Distancia relativa de objetos respecto a la ISS')
plt.xlabel('Tiempo (Índice de fila)')
plt.ylabel('Distancia (unidades)')
plt.legend(loc='upper right', fontsize='small')
plt.grid(True)
plt.tight_layout()
plt.show()

# Guardar distancias en un archivo Excel
output_file_path_distances = 'distancias_relativas_iss.xlsx'
distances.to_excel(output_file_path_distances, index=False)
print(f"Distancias relativas guardadas en: {output_file_path_distances}")