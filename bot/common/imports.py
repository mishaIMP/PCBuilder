import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, disable_web_page_preview=True)
dp = Dispatcher(storage=MemoryStorage())
