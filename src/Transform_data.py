import pandas as pd
import json
from datetime import datetime


SAVE_PATH = 'WA_Campaigns_Report_Creation/data/processed'
COUNTRIES_LIST = ['ARG']


def parse_json(response: str) -> str:

    response =  re.sub(r'\\(?!n)', '', response)
    response_data = ''

    if response[:2] != '{"':
        return response
        
    # Cleaning Json
    if response[-1] != '}':
        response = response + '}'

    if response[-2] != '"' and response[-5:-1] != 'null':
        response = response[:-1] + '"}'

    if response[-4:] == '","}':
        response = response[:-4] + '"}'
        
    response = response.replace('}"}', '}}')
    
    try:
        json_data = json.loads(response)
        response_data = extracting_json_data(json_data)
        return response_data
    
    except json.JSONDecodeError as e:
        # print(response)
        # print(f"Todavía hay un error: {e}")
        response = re.sub(r"(?<![{:}'])\"(?![{:}'])", r'\"', response)
        # print(response)

        try:
            json_data = json.loads(response)
            response_data = extracting_json_data(json_data)
            return response_data
        
        except json.JSONDecodeError as e:
            return ''

def extracting_json_data(data: dict) -> str: 
    response = ''

    #Body strcuture: Simple answer
    if 'Body' in data.keys():
        response = data['Body']
        return response

    # Payload: Button response
    if 'Payload' in data.keys():
        response = data['Payload']
        return response
    
    # Multimedia resource
    if 'Sha256' in data.keys() or 'Id' in data.keys():

        if 'Caption' in data.keys():
            response = data['Caption']

        if 'FileName' in data.keys():
            response = response +'\n'+ data['FileName'] if response != '' else data['FileName']
        
        if  'MimeType' in data.keys():       
            response = response + '\n' + 'Recurso multimedia enviado: ' + data['MimeType'] if response != '' else 'Recurso multimedia enviado: ' + data['MimeType']

        return response
    
    return response


def transform_responses(responses_df: pd.DataFrame) -> pd.DataFrame:

    responses_df = responses_df.drop(['locale', 'ChannelId'], axis=1)

    # Setting datatypes for columns
    responses_df['mobile'] = responses_df['mobile'].fillna(0).astype(int)
    responses_df['message_hcp_reply'] = responses_df['message_hcp_reply'].astype(str)
    responses_df['createddate'] = pd.to_datetime(responses_df['createddate'], errors='coerce')
    responses_df['ConversationId'] = responses_df['ConversationId'].astype(str)
    responses_df['ChatMessagingMOLogId'] = responses_df['ChatMessagingMOLogId'].astype(int)

    # Extract response
    responses_df['message_hcp_reply'] = responses_df['message_hcp_reply'].apply(parse_json)

    # Añadir una columna con el orden de aparición de los IDs compartidos
    responses_df['message_number'] = responses_df.groupby('ConversationId').cumcount() + 1

    # Rename columns for clarity
    responses_df = responses_df.rename(columns={
        'mobile': 'mobile_number',
        'message_hcp_reply': 'hcp_message_reply',
        'ConversationId': 'conversation_id',
        'ChatMessagingMOLogId': 'message_log_id',
        'message_number': 'message_order',
        'createddate': 'conversation_date'
    })

    # Reorder columns
    responses_df = responses_df[[
        'message_log_id',
        'conversation_id',
        'mobile_number',
        'hcp_message_reply',
        'conversation_date',
        'message_order'
    ]]

    return responses_df

def transform_conversations(responses_df: pd.DataFrame) -> pd.DataFrame:

    conversations_df = responses_df[['conversation_id', 'mobile_number', 'message_date']].copy()

    conversations_df  = conversations_df.drop_duplicates(subset=['conversation_id'], keep='first')

    conversations_df['campaing_id'] = ''
    conversations_df['conversation'] = ''
    conversations_df['conversation_category'] = ''
    conversations_df['conversation_feeling'] = ''
    conversations_df['conversation_need'] = ''
    conversations_df['support_type'] = ''

    conversations_df = conversations_df.rename(columns={
        'conversation_id': 'conversation_id',
    })

    conversations_df = conversations_df[[
        'conversation_id', 
        'mobile_number', 
        'conversation_date', 
        'campaing_id', 
        'conversation', 
        'conversation_category', 
        'conversation_feeling', 
        'conversation_need', 
        'support_type']]

    conversations_ids = conversations_df['conversation_id'].unique().tolist()



for country in COUNTRIES_LIST:
    df = pd.read_csv(f'{SAVE_PATH}/{country}_WA_Responses.csv', sep=',')

    # DF with the transformed responses
    responses_df = transform_responses(df)

