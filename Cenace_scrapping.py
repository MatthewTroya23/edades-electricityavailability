import pandas as pd
import matplotlib.pyplot as plt
from fuzzywuzzy import process, fuzz
import easyocr
from PIL import Image
import cv2
import numpy as np
import requests
import xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import os
from datetime import datetime


session = requests.Session()
retry = Retry(connect=5, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

url = "https://www.cenace.gob.ec/info-operativa/InformacionOperativa_archivos/filelist.xml"
# Descargar el archivo XML
response = session.get(url, verify=False)  # Verifica el SSL si es necesario
with open("filelist.xml", "wb") as file:
    file.write(response.content)



# Cargar el archivo XML
tree = ET.parse("filelist.xml")
root = tree.getroot()

# Extraer las rutas de las imágenes PNG
image_files = []
for file in root.findall(".//o:File", namespaces={"o": "urn:schemas-microsoft-com:office:office"}):
    href = file.get("HRef")
    if href.endswith(".png"):
        image_files.append(href)

print("Imágenes encontradas:", image_files)

# URL base para construir la URL completa de cada imagen
base_url = "https://www.cenace.gob.ec/info-operativa/InformacionOperativa_archivos/"

# Crear un directorio para guardar las imágenes
os.makedirs("imagenes_descargadas", exist_ok=True)

# Descargar imagen
image_url = base_url + 'image088.png'
img_data = requests.get(image_url, verify=False).content  # verify=False para SSL
image_path = os.path.join("imagenes_descargadas", 'image088.png')

with open(image_path, "wb") as img_file:
    img_file.write(img_data)
print(f"Descargada: {image_path}")

# Cargar la imagen original
image_path = 'imagenes_descargadas\image088.png'
image = cv2.imread(image_path)

# Región de la gráfica de barras (ajusta según la imagen)
roi_bar_chart = image[0:800, 525:1200]

# Convertir a escala de grises
gray = cv2.cvtColor(roi_bar_chart, cv2.COLOR_BGR2GRAY)

# Aumentar el contraste
contrasted = cv2.convertScaleAbs(gray, alpha=1.6, beta=0)
contrasted2 = cv2.convertScaleAbs(gray, alpha=4, beta=0) #Los últimos dos valores siempre se combinan con la barra, por eso se busca desaparecerla
contrasted3 = cv2.convertScaleAbs(gray, alpha=2, beta=0) #Para texto

bar_regions = [
    contrasted[0:40, 175:1200], contrasted[39:58, 175:1200],contrasted[60:80, 175:1200],contrasted[80:105, 175:1200],contrasted[105:125, 175:1200]
    , contrasted[127:152, 175:1200], contrasted[152:175, 175:1200], contrasted[175:197, 175:300], contrasted[199:220, 175:300], contrasted[222:245, 175:300],
    contrasted[245:267, 175:300], contrasted[270:295, 175:300], contrasted[295:315, 175:300], contrasted[315:340, 175:250], contrasted[340:362, 175:250],
    contrasted[365:385, 175:250], contrasted[390:410, 175:250], roi_bar_chart[412:435, 191:250], roi_bar_chart[435:455, 191:250]
]

# Lista para almacenar los resultados de OCR de cada barra
results_numbers = []


# Iterar sobre cada región de barra
for i in bar_regions:
    # Recortar la región de cada barra
    scale_percent = 500  # Aumentar el tamaño al 200%
    height, width = i.shape[:2]
        
    # Calcula el nuevo tamaño
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)
    dim = (new_width, new_height)
    resized = cv2.resize(i, dim, interpolation=cv2.INTER_LINEAR)
    # Aplicar OCR en la región de la barra recortada
    reader = easyocr.Reader(['es',"en"])  # Indica el idioma de la imagen
    result = reader.readtext(resized, detail=0, allowlist='0123456789')  # `detail=0` para obtener solo el texto
    
    # Añadir el resultado a la lista
    results_numbers.append(result)

bar_regions = [
    contrasted3[0:40, 0:175], contrasted3[39:58, 0:175],contrasted3[60:80, 0:175],contrasted3[80:105, 0:175],contrasted3[105:125, 0:175]
    , contrasted3[127:152, 0:175], contrasted3[152:175, 0:175], contrasted3[175:197, 0:175], contrasted3[199:220, 0:175], contrasted3[222:245, 0:175],
    contrasted3[245:267, 0:175], contrasted3[270:295, 0:175], contrasted3[295:315, 0:175], contrasted3[315:340, 0:175], contrasted3[340:362, 0:175],
    contrasted3[365:385, 0:175], contrasted3[390:410, 70:175], contrasted3[412:435, 50:175], contrasted3[435:455, 0:175]
]

# Lista para almacenar los resultados de OCR de cada barra
results = []

# Iterar sobre cada región de barra
for i in bar_regions:
    # Recortar la región de cada barra
    scale_percent = 350  # Aumentar el tamaño al 200%
    height, width = i.shape[:2]
        
    # Calcula el nuevo tamaño
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)
    dim = (new_width, new_height)
    resized = cv2.resize(i, dim, interpolation=cv2.INTER_LINEAR)
    # Aplicar OCR en la región de la barra recortada
    reader = easyocr.Reader(['es'])  # Indica el idioma de la imagen
    result = reader.readtext(resized, detail=0)  # `detail=0` para obtener solo el texto
    
    # Añadir el resultado a la lista
    results.append(result)

results_Nombres = []

# Lista de nombres esperados
expected_names = ["CNEL EP BOLIVAR", "CNEL EP GUAYAQUIL", "EE. Quito", "CNEL EP GUAYAS LOS RIOS", "CNEL EP MANABI", "CNEL EP EL ORO", "EE. Centro Sur",
                  "EE. Regional Sur", "CNEL EP SANTA ELENA", "CNEL EP MILAGRO", "CNEL EP SANTO DOMINGO", "EE.Ambato", "CNEL EP SUCUMBIOS", "EMELNORTE",
                   "ELEPCO", "CNEL EP ESMERALDAS", "CNEL EP LOS RIOS", "EE. Riobamba", "CNEL EP BOLIVAR", "EE.Azogues" ]

for result in results:
    # Texto detectado por OCR
    detected_text = result[0]
    best_match = process.extractOne(detected_text, expected_names, scorer=fuzz.token_set_ratio)
    results_Nombres.append(best_match[0])

results_demand = [int(num[0]) for num in results_numbers]

# Crear el DataFrame
data = pd.DataFrame({
    'Empresa': results_Nombres,
    'Demanda': results_demand  
})

total_demanda = data['Demanda'].sum()
print("Total de demanda:", total_demanda)

# Guardar CSV
registro = {
    "Hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

for i, row in data.iterrows():
    registro[row['Empresa']] = row['Demanda']

# Convertir el registro a un DataFrame de una sola fila
registro_df = pd.DataFrame([registro])

# Nombre del archivo CSV
filename = "demanda_empresas_cenace.csv"

# Guardar el DataFrame en el CSV, agregando una fila en cada ejecución
registro_df.to_csv(filename, mode='a', index=False, header=not pd.io.common.file_exists(filename))

print(f"Datos guardados exitosamente en {filename}")
