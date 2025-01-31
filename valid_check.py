from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
import re
import asyncio

# Инициализация бота и диспетчера
bot = Bot(token="8105577356:AAGOWwevyeT5ZNfl4N8zsLxRyKK1N8jGLoY")
dp = Dispatcher()

# Регулярные выражения для проверки форматов
CHAT_ID_REGEX = re.compile(r"^-100\d+$")  # ID чата начинается с -100 и содержит только цифры
USERNAME_REGEX = re.compile(r"^@[A-Za-z0-9_]{5,32}$")  # Username начинается с @ и содержит 5-32 символа

# Хранилище 
user_data = {}

def validate_chat_entity(entity: str) -> str:
    """Проверяет формат чата и возвращает тип (chat_id/username) или 'invalid'"""
    entity = entity.strip()
    if CHAT_ID_REGEX.fullmatch(entity):  # Проверка на ID чата
        return "chat_id"
    if USERNAME_REGEX.fullmatch(entity):  # Проверка на username
        return "username"
    return "invalid"  # Некорректный формат

async def process_entities(message: types.Message, entities: list):
    """Обрабатывает список чатов, проверяет их и сохраняет в user_data"""
    user_id = message.from_user.id
    valid_entities = []  # Валидные чаты
    errors = []  # Ошибки формата
    
    for entity in entities:
        if not entity.strip():  # Пропуск пустых строк
            continue
            
        result = validate_chat_entity(entity)
        
        if result == "invalid":
            errors.append(f"Некорректный формат: {entity}")  # Добавление ошибки
        else:
            valid_entities.append(entity)  # Добавление валидного чата
    
    user_data[user_id] = valid_entities  # Сохранение данных для пользователя
    
    response = []
    if valid_entities:
        response.append("Успешно добавлено:")  # Успешные добавления
        response.extend(valid_entities)
    if errors:
        response.append("\n Ошибки:")  # Ошибки
        response.extend(errors)
    
    await message.answer("\n".join(response))  # Отправка результата пользователю

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка команды /start"""
    await message.answer(
        "Отправьте мне список чатов для парсинга:\n"
        "- ID чата (начинается с -100)\n"
        "- @username канала\n"
        "- Или .txt файл со списком"
    )

@dp.message(lambda message: message.content_type == ContentType.TEXT)
async def handle_text(message: types.Message):
    """Обработка текстового сообщения (список чатов)"""
    entities = message.text.split('\n')  # Разделение текста на строки
    await process_entities(message, entities)  # Обработка списка

@dp.message(lambda message: message.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    """Обработка .txt файла"""
    if not message.document.file_name.endswith('.txt'):  # Проверка расширения файла
        await message.answer("Поддерживаются только .txt файлы")
        return
    
    file = await bot.get_file(message.document.file_id)  # Получение файла
    downloaded_file = await bot.download_file(file.file_path)  # Скачивание файла
    content = downloaded_file.read().decode('utf-8')  # Чтение содержимого
    
    entities = content.split('\n')  # Разделение на строки
    await process_entities(message, entities)  # Обработка списка

@dp.message()
async def handle_other_types(message: types.Message):
    """Обработка всех остальных типов сообщений"""
    await message.answer("Пожалуйста, отправьте текст или .txt файл")

async def main():
    """Запуск бота"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())  