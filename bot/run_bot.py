import asyncio
import logging
import sys

from bot.common.imports import dp, bot
from bot.handlers.add import register_add_handlers
from bot.handlers.find import register_find_handlers
from bot.handlers.my import register_my_handlers
from bot.handlers.start import register_start_handler


async def main() -> None:
    register_start_handler(dp)
    register_add_handlers(dp)
    register_find_handlers(dp)
    register_my_handlers(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
