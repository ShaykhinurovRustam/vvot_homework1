import json
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from config import TELEGRAM_TOKEN
from handlers import setup_handlers

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
setup_handlers(dp)

async def process_update(update_data: dict):
    Bot.set_current(bot)
    Dispatcher.set_current(dp)
    
    update = Update.to_object(update_data)
    await dp.process_update(update)

def handler(event, context):
    if event.get('httpMethod') == 'POST':
        body = event.get('body')
        if not body:
            return {'statusCode': 400, 'body': 'No body received'}

        try:
            update_data = json.loads(body)
        except json.JSONDecodeError:
            return {'statusCode': 400, 'body': 'Invalid JSON'}

        asyncio.run(process_update(update_data))
        return {'statusCode': 200, 'body': 'OK'}

    return {'statusCode': 405, 'body': 'Method Not Allowed'}