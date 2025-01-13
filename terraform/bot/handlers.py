from aiogram import Dispatcher, types
from services.gpt import get_gpt_response
from services.ocr import extract_text_from_photo

async def handle_start(message: types.Message):
    await message.answer('Я помогу подготовить ответ на экзаменационный вопрос по дисциплине \'Операционные системы\'.\n'
                         'Пришлите мне фотографию с вопросом или наберите его текстом.')

async def handle_message(message: types.Message):
    try:
        response = await get_gpt_response(message.text)
        await message.answer(response)
    except Exception:
        await message.answer('Я не смог подготовить ответ на экзаменационный вопрос.')

async def handle_photo(message: types.Message):
    if len(message.photo) > 1:
        await message.answer('Я могу обработать только одну фотографию.')
        return

    try:
        photo = message.photo[-1]
        file = await photo.get_file()
        photo_data = await file.download()

        text = await extract_text_from_photo(photo_data)

        if text:
            response = await get_gpt_response(text)
            await message.answer(response)
        else:
            await message.answer('Я не могу обработать эту фотографию.')
    except Exception:
        await message.answer('Произошла ошибка при обработке фотографии.')

async def handle_unsupported(message: types.Message):
    await message.answer('Я могу обработать только текстовое сообщение или фотографию.')

def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_start, commands=['start', 'help'])
    dp.register_message_handler(handle_message, content_types=types.ContentType.TEXT)
    dp.register_message_handler(handle_photo, content_types=types.ContentType.PHOTO)
    dp.register_message_handler(handle_unsupported, content_types=types.ContentType.ANY)