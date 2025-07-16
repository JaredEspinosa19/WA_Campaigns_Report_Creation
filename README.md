# Carga y analisis de respuestas WA

Este proceso sirve para analizar las respuestas de WA de los canales de Sanofi y actualizar la fuente principal donde se guardan estos datos. A día de hoy los datos se tienen en archivos de texto plano. En un futuro, se presenten hacer una conexion a Sharepoint 


## Prerequisitos
- Inputs:
  - Datos sobre los envío de la campaña: Archivo CSV
  - Datos sobre los shots que componen la campaña (Nombre del shot + Día y Hora de envío)


## Flujo del proceso

    1. Actualización Fuente
        1. Se lee el arhivo con las conversaciones de los últimos N días
        1. Se aplica un ETL, el cual transforma las estructura de estos a otros
        1. Se verifica que esos registros de datos no existan dentro de sus conjuntos de datos correspondientes.
          - Historic Messages
          - Historic Conversations
        1. Si no existen dentro de los registros, se actualizan
    
    2. Analisis de las respuestas (Clasificación)
       1. Se lee el archivo que contiene las conversaciones (Cada lunes y miercoles)
       2. Se buscan dentro del histórico de las conversaciones aquellas que no han sido clasificadas anteriormente
       3. Se pasan cada una de estas conversaciones al LLM para clasificar los textos
       4. Se actualiza la base de datos (o CSV con los nuevos datos de las conversaciones)

    3. Creación del reporte    
       1. Se realiza una copia del template de Whats App
       2. Se copia la nueva estructura de los datos de la campaña en la tabla correspondiente
       3. Se copia el análisis de las conversaciones en la tabla correspondiente
       4. Se guarda el archivo Excel en la carpeta de reportes