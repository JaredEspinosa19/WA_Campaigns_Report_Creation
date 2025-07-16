import pandas as pd
import os


DB_PATH = 'C:/Users/choc-/OneDrive/Escritorio/WA_Campaigns_Report_Creation/data/db'

COUNTRIES = ['ARG']

def get_ids_db(messages_df: pd.DataFrame, conversations_df: pd.DataFrame) -> tuple:

    messages_ids = messages_df['message_log_id'].unique().tolist()
    conversations_ids = conversations_df['conversation_id'].unique().tolist()

    return messages_ids, conversations_ids


def write_new_rows_to_db(orignal_db: pd.DataFrame, new_rows: pd.DataFrame, db_name) -> None:

    print(f'Adding {len(new_rows)} new rows to {db_name}')

    combined_df = pd.concat([orignal_db, new_rows], ignore_index=True)
    
    combined_df['conversation_date'] = pd.to_datetime(combined_df['conversation_date'], errors='coerce')
    combined_df = combined_df.sort_values(by='conversation_date', ascending=True).reset_index(drop=True)
    
    combined_df.to_csv(os.path.join(DB_PATH, f'{db_name}'), index=False)

def update_db(responses_df: pd.DataFrame, conversations_df: pd.DataFrame) -> None:

    for country in COUNTRIES:

        messages_df = pd.read_csv(os.path.join(DB_PATH, f'{country}_Historic_Messages.csv'))
        conversations_df = pd.read_csv(os.path.join(DB_PATH, f'{country}_Historic_Conversations.csv'))

        # Get existing IDs from the database
        messages_ids, conversations_ids = get_ids_db(messages_df, conversations_df)

        # Filter out existing messages
        new_messages_df = responses_df[~responses_df['message_log_id'].isin(messages_ids)]
        new_conversations_df = conversations_df[~conversations_df['conversation_id'].isin(conversations_ids)]

        # Append new data to the CSV files
        if not new_messages_df.empty:
            write_new_rows_to_db(messages_df, new_messages_df, f'{country}_Historic_Messages.csv')
        
        if not new_conversations_df.empty:
            write_new_rows_to_db(conversations_df, new_conversations_df, f'{country}_Historic_Conversations.csv')