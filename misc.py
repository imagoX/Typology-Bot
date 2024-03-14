import logging

# Logging
from aiogram import Bot, Dispatcher, types

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

# Bot configs
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
