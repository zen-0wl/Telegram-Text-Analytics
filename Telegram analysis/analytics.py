import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
import pandas as pd
import nltk
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
import pandas as pd
import os 

# values with own API ID, API hash, and phone details
api_id = "--------"
api_hash = '-------------------------------'
phone_number = '+60'

group_name = -1001462876169 # relevant group ID

start_time = datetime.now() - timedelta(hours=24)
flag = 0
max_messages = 200

# reads word lists from files
def read_word_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()
    return set(words)

# calculates sentiment score for a message
def calculate_sentiment_score(message, positive_words, negative_words, negation_words, booster_inc_words, booster_decr_words):
    sentiment_score = 0

    # splits message into words
    words = message.split()

    for word in words:
        if word.lower() in positive_words:
            sentiment_score += 0.2
        elif word.lower() in negative_words:
            sentiment_score -= 0.2
        elif word.lower() in negation_words:
            sentiment_score = -sentiment_score
        elif word.lower() in booster_inc_words:
            sentiment_score += 0.2
        elif word.lower() in booster_decr_words:
            sentiment_score -= 0.2
    
    return max(0, min(1, (sentiment_score + 1) / 2)) # normalise sentiment scores within range [0, 1.0] 

async def get_group_messages():
    df = pd.DataFrame({'Data': [''], 'name': [''], 'mobile': ['']})
    df1 = pd.DataFrame({'Data': [''], 'name': [''], 'mobile': ['']})
    client = TelegramClient('session_name', api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))
    
    positive_words = read_word_list('positive.txt')
    negative_words = read_word_list('negative.txt')
    negation_words = read_word_list('negation.txt')
    booster_inc_words = read_word_list('booster_inc.txt')
    booster_decr_words = read_word_list('booster_decr.txt')
    
    # Testings with other keywords
    keywords = ['Khan Younis', 'gaza', 'palestine', 'conflict', 'peace', 'war', 'crisis', 'refugee', 'humanitarian', 'truce', 'ceasefire', 'violence', 'happy', 'good', 'displacement', 'houses', 'IDF']
    
    # Added keywords to +ve and -ve lists
    positive_words.update(keywords)
    
     # ID token of specific group
    group = await client.get_entity(group_name)
    date_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    yesterday = date_today - timedelta(days=5)
    
    messages = []
    async for message in client.iter_messages(group, limit=max_messages):
        if any(keyword.lower() in message.text.lower() for keyword in keywords):
            sentiment_score = calculate_sentiment_score(
                message.text,
                positive_words,
                negative_words,
                negation_words,
                booster_inc_words,
                booster_decr_words
            )
            print(f'Text: {message.text}\nSentiment Score: {sentiment_score}\n')


# run messages using asyncio
asyncio.run(get_group_messages())