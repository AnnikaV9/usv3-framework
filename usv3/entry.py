#
#  Entry point for the bot, can be run with the following ways:
#   $ poetry run bot
#   $ ./.venv/bin/bot
#   $ ./.venv/bin/python .venv/bin/bot
#

import os
import uvloop
import atexit
import argparse
import importlib.metadata
from ruamel.yaml import YAML
from loguru import logger

import usv3.bot


@atexit.register
def exit_handler() -> None:
    logger.info("usv3 has stopped")


def load_config() -> dict[str, str]:
    try:
        yaml = YAML(typ="safe")
        with open("config/core_config.yml", "r") as core_config:
            return yaml.load(core_config)

    except Exception as e:
        logger.error(f"Failed to read config ({type(e).__name__}: {e})")
        raise SystemExit(1)


def parse_overrides() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="help")
    parser.add_argument("--debug", action="store_true", default=argparse.SUPPRESS)
    parser.add_argument("--channel", type=str, default=argparse.SUPPRESS)
    parser.add_argument("--nick", type=str, metavar="NICKNAME", default=argparse.SUPPRESS)
    parser.add_argument("--password", type=str, default=argparse.SUPPRESS)
    parser.add_argument("--server", type=str, default=argparse.SUPPRESS)
    try:
        return parser.parse_args()

    except SystemExit:
        os._exit(1)


def main() -> None:
    overrides = parse_overrides()
    logger.info(f"Starting usv3 (v{importlib.metadata.version('usv3')})")
    core_config = load_config()
    core_config.update(vars(overrides))
    try:
        bot = usv3.bot.Bot(core_config)
        uvloop.run(bot.main())

    except KeyboardInterrupt:
        logger.warning("Received KeyboardInterrupt")
        raise SystemExit(0)

    except Exception as e:
        exc_logger = logger.exception if core_config["debug"] else logger.error
        exc_logger(f"usv3 crashed due to a fatal error ({type(e).__name__}: {e})")
        raise SystemExit(1)
