#
#  Runner task for catching and logging module exceptions.
#

from typing import Callable
from loguru import logger

async def run(task: Callable, module: str, *args) -> None:
    try:
        logger.info(f"Module {module} triggered")
        await task(*args)

    except Exception as e:
        logger.error(f"Exception in module {module}: {e}")
