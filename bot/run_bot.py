import asyncio
import logging
import sys

from .common.imports import dp, bot
from .handlers.add import register_add_handlers
from .handlers.find import register_find_handlers
from .handlers.my import register_my_handlers
from .handlers.start import register_start_handler
from .middlewares.main import MainMiddleware


async def main() -> None:
    middleware = MainMiddleware()
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)

    register_start_handler(dp)
    register_add_handlers(dp)
    register_find_handlers(dp)
    register_my_handlers(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
