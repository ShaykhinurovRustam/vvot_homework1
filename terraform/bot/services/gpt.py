import aiohttp
import asyncio

from config import YANDEX_API_KEY, INSTRUCTION_URL, CATALOG_ID


POLL_URL = 'https://llm.api.cloud.yandex.net/operations/'
COMPLETION_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'

async def get_gpt_response(question):
    
    async with aiohttp.ClientSession() as session:
        async with session.get(INSTRUCTION_URL) as resp:
            instruction = await resp.text()
            
    messages = [
        {'role': 'system', 'text': instruction}, 
        {'role': 'user', 'text': question},
    ]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {YANDEX_API_KEY}',
        'x-folder-id': f'{CATALOG_ID}',
    }
    payload = {
        'modelUri': f'gpt://{CATALOG_ID}/yandexgpt-lite/latest',
        'completionOptions': {
            'stream': False,
            'temperature': 0.6,
            'maxTokens': 1000
        },
        'messages': messages,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(COMPLETION_URL, headers=headers, json=payload) as resp:
            data = await resp.json()
            completion_request_id = data['id']
           
    attempts = 0 
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(f'{POLL_URL}{completion_request_id}', headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get('done', False):
                        return data['response']['alternatives'][0]['message']['text']
                    
                    if attempts == 5:
                        return None
                    
                    attempts += 1
                    await asyncio.sleep(1)