import os
import pandas as pd
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from azure.storage.blob import BlobServiceClient

# Configuration of ENV's
DATASET = os.environ['KAGGLE_DATASET']
DATE_COLUMN = os.environ['KAGGLE_DATE_COLUMN']
CONTAINER_NAME = os.environ['AZURE_CONTAINER']
AZURE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']


# Autentication on Kaggle dataset
os.environ['KAGGLE_USERNAME'] = os.environ['KAGGLE_USERNAME']
os.environ['KAGGLE_KEY'] = os.environ['KAGGLE_KEY']

api = KaggleApi()
api.authenticate()


# Download dataset from Kaggle
api.dataset_download_files(DATASET, path='data_reemplazar', unzip=True)


# Leer CSV
csv_file = [f for f in os.listdir('data') if f.endswith('.csv')][0]
df = pd.read_csv(f'data/{csv_file}', parse_dates=[DATE_COLUMN])


# Connection to Azure
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# partition by date
for fecha, grupo in df.groupby(df[DATE_COLUMN].dt.date):
    nombre_archivo = f"proyecto_{fecha.strftime('%Y-%m-%d')}.csv"
    grupo.to_csv(nombre_archivo, index=False)
    with open(nombre_archivo, "rb") as data:
        blob_client = container_client.get_blob_client(nombre_archivo)
        blob_client.upload_blob(data, overwrite=True)




