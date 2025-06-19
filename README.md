# Creación de reportes de Campañas WA + Análisis de Respuestas


## Prerequisitos
- Inputs:
  - Datos sobre los envío de la campaña: Archivo CSV
  - Datos sobre los shots que componen la campaña (Nombre del shot + Día y Hora de envío)


## Flujo del proceso

    1. Restructuración Archivo CSV
        1. Se lee el archivo CSV sobre los datos de campaña.
        1. Se aplica un ETL, el cual transforma los datos de una estructura a otra
    
    2. Analisis de las respuestas (Clasificación)
       1. Se lee el archivo txt con los datos de cada uno de los shots de la campaña
       2. Se buscan dentro del histórico de las conversacion (API o leyendo un archivo), y se filtran aquellos mensajes por shot, que se encuentren dentro de las siguientes 24 horas de enviado después de que el shot se mando
       3. Se pasan cada una de estas conversaciones al LLM para clasificar los textos
       4. Se actualiza la base de datos (o CSV con los nuevos datos de las conversaciones)

    3. Creación del reporte    
       1. Se realiza una copia del template de Whats App
       2. Se copia la nueva estructura de los datos de la campaña en la tabla correspondiente
       3. Se copia el análisis de las conversaciones en la tabla correspondiente
       4. Se guarda el archivo Excel en la carpeta de reportes