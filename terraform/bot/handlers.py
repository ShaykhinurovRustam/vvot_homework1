from aiogram import Dispatcher, types
from services.gpt import get_gpt_response
from services.ocr import extract_text_from_photo

import base64
from io import BytesIO


async def handle_start(message: types.Message):
    await message.answer('Я помогу подготовить ответ на экзаменационный вопрос по дисциплине "Операционные системы".\n'
                         'Пришлите мне фотографию с вопросом или наберите его текстом.')

async def handle_message(message: types.Message):
    try:
        response = await get_gpt_response(message.text)
        await message.answer(response)
    except Exception as e:
        await message.answer(f'Я не смог подготовить ответ на экзаменационный вопрос.')

async def handle_photo(message: types.Message):
    if message.media_group_id:
        await message.answer('Я могу обработать только одну фотографию.')
        return

    try:
        photo = message.photo[-1]
        photo_bytes = BytesIO()
        
        await photo.download(destination=photo_bytes)
        
        photo_bytes.seek(0)
        b64_photo = base64.b64encode(photo_bytes.read()).decode('utf-8')

        text = await extract_text_from_photo(b64_photo)
        
        if text:
            response = await get_gpt_response(text)
            await message.answer(response)
        else:
            await message.answer('Я не могу обработать эту фотографию.')
    except Exception as ex:
        await message.answer(f'Произошла ошибка при обработке фотографии.')

async def handle_unsupported(message: types.Message):
    await message.answer('Я могу обработать только текстовое сообщение или фотографию.')

def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_start, commands=['start', 'help'])
    dp.register_message_handler(handle_message, content_types=types.ContentType.TEXT)
    dp.register_message_handler(handle_photo, content_types=types.ContentType.PHOTO)
    dp.register_message_handler(handle_unsupported, content_types=types.ContentType.ANY)