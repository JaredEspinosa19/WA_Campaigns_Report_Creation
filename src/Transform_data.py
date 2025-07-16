import pandas as pd
import json
from datetime import datetime
import re
from Update_DB import update_db

SAVE_PATH = 'C:/Users/choc-/OneDrive/Escritorio/WA_Campaigns_Report_Creation/data/inputs'
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
        'message_hcp_reply': 'message',
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
        'message',
        'conversation_date',
        'message_order'
    ]]

    responses_df['conversation_date'] = pd.to_datetime(responses_df['conversation_date'], errors='coerce')
    responses_df = responses_df.sort_values(by='conversation_date', ascending=True).reset_index(drop=True)

    return responses_df

def transform_conversations(responses_df: pd.DataFrame) -> pd.DataFrame:

    conversations_df = responses_df[['conversation_id', 'mobile_number', 'conversation_date']].copy()

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

    for id in conversations_ids:
        try:
            messages_text = responses_df[responses_df['conversation_id'] == id].sort_values(by='message_order')['message'].astype(str).tolist()
            if not messages_text:
                raise ValueError("messages_text is an empty list")
        except Exception as e:
            print(f"Error processing conversation_id {id}: {e}")
            messages_text = []
        
        final_message = '\n'.join(messages_text) if len(messages_text) > 0 else ''

        conversations_df.loc[conversations_df['conversation_id'] == id, 'conversation'] = final_message
        # Asegurarse que 'conversation_date' es tipo fecha
        conversations_df['conversation_date'] = pd.to_datetime(conversations_df['conversation_date'], errors='coerce')
        conversations_df = conversations_df.sort_values(by='conversation_date', ascending=True).reset_index(drop=True)
    
    return conversations_df


def main():
    for country in COUNTRIES_LIST:
        df = pd.read_csv(f'{SAVE_PATH}/{country}_WA_Responses.csv', sep=',')

        # DF with the transformed responses
        responses_df = transform_responses(df)

        # DF with the transformed conversations
        conversations_df = transform_conversations(responses_df)

        update_db(responses_df, conversations_df)

main()
