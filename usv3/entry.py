#
#  Entry point for the bot, can be run with the following ways:
#   $ poetry run bot
#   $ ./.venv/bin/bot
#   $ ./.venv/bin/python .venv/bin/bot
#

import traceback
import asyncio
import uvloop
from loguru import logger

import usv3.bot

def main() -> None:
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        bot = usv3.bot.Bot()
        asyncio.run(bot.main())

    except KeyboardInterrupt:
        raise SystemExit

    except Exception as e:
        exc_module = e.__class__.__module__
        exc_name = e.__class__.__name__ if exc_module is None or exc_module == str.__class__.__module__ else f"{exc_module}.{e.__class__.__name__}"
        logger.critical(f"{exc_name}: {e}")
