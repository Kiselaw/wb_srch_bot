import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

from wb_parse import parse

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    """
    Обработчик для команды `/start`.
    """
    await message.reply('Привет! Я - WBSRCHbot!\nПомогу найти тебе товар с '
                        'нужным артикулом на wildberries.ru.')


@dp.message_handler(commands=['start', 'help'])
async def send_help_information(message: types.Message) -> None:
    """
    Обработчик для команды `/help`.
    """
    await message.reply('Формат запроса: артикул (число) '
                        'название (тип, вид и т.п.).')


@dp.message_handler()
async def echo(message: types.Message) -> None:
    """
    Обработчик запросов пользователей.
    """
    user_request: str = message.text.split()
    vendor_code: str = user_request[0]
    product_name: str = ' '.join(user_request[1:])
    try:
        int(user_request[0])
    except ValueError:
        await message.answer('Неправильный формат запроса. '
                             'Для получения образца отправьте /help.')
    else:
        response = parse(vendor_code, product_name)
        if len(response) > 0:
            await message.answer(f'Страница: {response[0][0]}, '
                                 f'позиция {response[0][1]}.')
        else:
            await message.answer('Товар, к сожалению, не найден.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
