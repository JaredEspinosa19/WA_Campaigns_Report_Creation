import pandas as pd
import time
import os

USER = 'U1058105'

INPUT_DIRECTORY_PATH = f"C:/Users/{USER}/OneDrive - Sanofi/Shared Documents - OCE Execution/CampañasESLAT/Operación (Exceution)/Automations/Reportes SFMC - WhatsApp/Entradas"
OUTPUT_DIRECTORY_PATH = f"C:/Users/{USER}/OneDrive - Sanofi/Shared Documents - OCE Execution/CampañasESLAT/Operación (Exceution)/Automations/Reportes SFMC - WhatsApp/Procesados"

def find_Sent_Dates(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

    # Asegurarse de que df2 tenga las columnas destino
    if 'Sent' not in df2.columns:
        df2['Sent'] = None
    if 'Sent_date' not in df2.columns:
        df2['Sent_date'] = None
    
    # Definir las columnas para la coincidencia
    cols_coincidencia = ['mobilenumber', 'shot']
    
    # Iterar sobre cada fila en df2
    for idx, fila in df2.iterrows():
        # Crear condición para las columnas de coincidencia (mobilenumber y shot)
        condicion = True
        for col in cols_coincidencia:
            if col in df1.columns and col in df2.columns:
                condicion = condicion & (df1[col] == fila[col])
        
        # Añadir condición para la columna status con valor 'failed'
        condicion = condicion & (df1['status'] == 'failed')
        
        # Filtrar df1 con las condiciones
        coincidencias = df1[condicion]
        
        # Verificar si hay coincidencias
        if not coincidencias.empty:
            # Si hay coincidencia: Sent = 0 y Sent_date = valor de eventdate
            df2.loc[idx, 'Sent'] = 0
            if 'eventdate' in coincidencias.columns:
                df2.loc[idx, 'Sent_date'] = coincidencias['eventdate'].values[0]
        else:
            # No hay coincidencia: solo Sent = 1
            df2.loc[idx, 'Sent'] = 1
    
    return df2

def find_Delivered_Dates(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

    # Asegurarse de que df2 tenga las columnas destino
    if 'Delivered' not in df2.columns:
        df2['Delivered'] = None
    if 'Delivered_Date' not in df2.columns:
        df2['Delivered_Date'] = None
    
    # Definir las columnas para la coincidencia
    cols_coincidencia = ['mobilenumber', 'shot']
    
    # Iterar sobre cada fila en df2
    for idx, fila in df2.iterrows():
        # Crear condición para las columnas de coincidencia (mobilenumber y shot)
        condicion = True
        for col in cols_coincidencia:
            if col in df1.columns and col in df2.columns:
                condicion = condicion & (df1[col] == fila[col])
        
        # Añadir condición para la columna status con valor 'delivered'
        condicion = condicion & (df1['status'] == 'delivered')
        
        # Filtrar df1 con las condiciones
        coincidencias = df1[condicion]
        
        # Verificar si hay coincidencias
        if not coincidencias.empty:
            # Si hay coincidencia: Delivered = 1 y Delivered_Date = valor de eventdate
            df2.loc[idx, 'Delivered'] = 1
            if 'eventdate' in coincidencias.columns:
                df2.loc[idx, 'Delivered_date'] = coincidencias['eventdate'].values[0]
        else:
            # No hay coincidencia: solo Delivered = 0
            df2.loc[idx, 'Delivered'] = 0
    
    return df2

def find_Read_Dates(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

    # Asegurarse de que df2 tenga las columnas destino
    if 'Read' not in df2.columns:
        df2['Read'] = None
    if 'Read_date' not in df2.columns:
        df2['Read_date'] = None
    
    # Definir las columnas para la coincidencia
    cols_coincidencia = ['mobilenumber', 'shot']
    
    # Iterar sobre cada fila en df2
    for idx, fila in df2.iterrows():
        # Crear condición para las columnas de coincidencia (mobilenumber y shot)
        condicion = True
        for col in cols_coincidencia:
            if col in df1.columns and col in df2.columns:
                condicion = condicion & (df1[col] == fila[col])
        
        # Añadir condición para la columna status con valor 'read'
        condicion = condicion & (df1['status'] == 'read')
        
        # Filtrar df1 con las condiciones
        coincidencias = df1[condicion]
        
        # Verificar si hay coincidencias
        if not coincidencias.empty:
            # Si hay coincidencia: Read = 1 y Read_date = valor de eventdate
            df2.loc[idx, 'Read'] = 1
            if 'eventdate' in coincidencias.columns:
                df2.loc[idx, 'Read_date'] = coincidencias['eventdate'].values[0]
        else:
            # No hay coincidencia: solo Read = 0
            df2.loc[idx, 'Read'] = 0
    
    return df2


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Convert the 'journey_createddate' and 'eventdate' columns to datetime format
    df['journey_createddate'] = pd.to_datetime(df['journey_createddate'], format='mixed')
    df['eventdate'] = pd.to_datetime(df['eventdate'], format='mixed')

    # Eliminate some meaningless words
    df.replace('<null>', None, inplace=True)
    df.replace('Running', 'Stopped', inplace=True)

    # Create aux df
    df_unique = df[['subscriberkey', 'mobilenumber', 'journey', 'shot']].drop_duplicates(subset='mobilenumber')
    df_unique['Sent'] = None
    df_unique['Sent_date'] = None
    df_unique['Delivered'] = None
    df_unique['Delivered_date'] = None
    df_unique['Read'] = None
    df_unique['Read_date'] = None

    df_final = find_Sent_Dates(df, df_unique)
    df_final = find_Delivered_Dates(df, df_final)
    df_final = find_Read_Dates(df, df_final)

    # Format the dates to 'YYYY-MM-DD HH:MM:SS'
    df_final['Sent_date'] = pd.to_datetime(df_final['Sent_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_final['Delivered_date'] = pd.to_datetime(df_final['Delivered_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_final['Read_date'] = pd.to_datetime(df_final['Read_date']).dt.strftime('%Y-%m-%d %H:%M:%S')

    df_final['Contacted'] = df_final['Sent'].apply(lambda x: '1' if x == 1 else '0')
    df_final['Interacted'] = df_final['Read'].apply(lambda x: '1' if x == 1 else '0')

    df_final = df_final[['subscriberkey', 'mobilenumber', 'journey', 'shot', 'Contacted', 'Interacted', 'Sent', 'Sent_date', 'Delivered', 'Delivered_date', 'Read', 'Read_date']]

    # Convert 'shot' column values to lowercase, remove spaces and underscores
    df_final['shot'] = df_final['shot'].str.lower().str.replace(' ', '').str.replace('_', '')
    
    return df_final
    # df_final.to_csv(OUTPUT_CSV_PATH, index=False, sep=',')


def read_csv_files(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(f'{file_path}', sep=',')
    print(f'Reading {file_path} ...')
    
    shots_list = df['shot'].unique()
    filtered_shots = [shot for shot in shots_list]
    
    print(filtered_shots)

    final_df = pd.DataFrame(columns=['subscriberkey', 'mobilenumber', 'journey', 'shot', 'Contacted', 'Interacted', 'Sent', 'Sent_date', 'Delivered', 'Delivered_date', 'Read', 'Read_date'])

    for shot in filtered_shots:
        df_filtered = df[df['shot'] == shot].copy()
        aux_df = filter_dataframe(df_filtered)
        final_df = pd.concat([final_df, aux_df], ignore_index=True)

    final_df.sort_values(by='shot', ascending=True, inplace=True)
    # final_df.to_csv(f'{OUTPUT_DIRECTORY_PATH}/{file_path}', index=False, sep=',')
    # print(f'{file_path} processed')

    return final_df
