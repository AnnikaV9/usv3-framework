#
#  Entry point for the bot, can be run with the following ways:
#   $ poetry run bot
#   $ ./.venv/bin/bot
#   $ ./.venv/bin/python .venv/bin/bot
#

import asyncio
import uvloop
import atexit
import importlib.metadata
from ruamel.yaml import YAML
from loguru import logger

import usv3.bot


@atexit.register
def exit_handler() -> None:
    logger.info("usv3 has stopped")


def load_config() -> dict:
    try:
        yaml = YAML(typ="safe")
        with open("config/core_config.yml", "r") as core_config:
            return yaml.load(core_config)

    except Exception as e:
        logger.error(f"Failed to read config ({type(e).__name__}: {e})")
        raise SystemExit


global core_config
core_config = load_config()


def main() -> None:
    try:
        logger.info(f"Starting usv3 ({importlib.metadata.version('usv3')})")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        bot = usv3.bot.Bot(core_config)
        asyncio.run(bot.main())

    except KeyboardInterrupt:
        logger.warning("Received KeyboardInterrupt")
        raise SystemExit

    except Exception as e:
        exc_logger = logger.exception if core_config["debug"] else logger.error
        exc_logger(f"usv3 crashed due to a fatal error ({type(e).__name__}: {e})")
