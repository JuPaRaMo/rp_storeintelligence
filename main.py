import os
import pandas as pd
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from azure.storage.blob import BlobServiceClient

# Configuración de variables de entorno
DATASET = os.environ['KAGGLE_DATASET']
DATE_COLUMN = os.environ['KAGGLE_DATE_COLUMN']
CONTAINER_NAME = os.environ['AZURE_CONTAINER']
AZURE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
KAGGLE_USERNAME = os.environ['KAGGLE_USERNAME']
KAGGLE_KEY = os.environ['KAGGLE_KEY']

# Autenticación en Kaggle
os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
os.environ['KAGGLE_KEY'] = KAGGLE_KEY

api = KaggleApi()
api.authenticate()

# Descargar dataset
os.makedirs('data', exist_ok=True)
api.dataset_download_files(DATASET, path='data', unzip=True)

# Detectar archivo CSV
csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
if not csv_files:
    raise FileNotFoundError("No se encontró ningún archivo CSV en la carpeta 'data'.")

csv_path = os.path.join('data', csv_files[0])  # Usa el primer CSV encontrado
df = pd.read_csv(csv_path, parse_dates=[DATE_COLUMN])

# Conexión a Azure
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Particionar por fecha y subir
for fecha, grupo in df.groupby(df[DATE_COLUMN].dt.date):
    nombre_archivo = f"proyecto_{fecha.strftime('%Y-%m-%d')}.csv"
    grupo.to_csv(nombre_archivo, index=False)
    with open(nombre_archivo, "rb") as data:
        blob_client = container_client.get_blob_client(nombre_archivo)
        blob_client.upload_blob(data, overwrite=True)
