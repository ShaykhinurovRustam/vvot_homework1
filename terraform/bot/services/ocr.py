import aiohttp

from config import YANDEX_API_KEY, CATALOG_ID

OCR_API_URL = 'https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText'


async def extract_text_from_photo(b64_photo):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {YANDEX_API_KEY}',
        'x-folder-id': f'{CATALOG_ID}',
    }
    payload = {
        'mimeType': 'JPEG',
        'languageCodes': ['ru'],
        'model': 'page',
        'content': b64_photo,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(OCR_API_URL, headers=headers, json=payload) as resp:
            data = await resp.json()
            photo_text = data['result']['textAnnotation']['fullText']
    
    return 'Ответь на билет:\n\n' + photo_text