"""
Runner task for catching and logging module exceptions.
"""

# stdlib
from typing import Callable

# external
from loguru import logger


async def run(task: Callable, module: str, debug: bool, *args) -> None:
    """
    Runs a module, catching and logging exceptions.
    """
    try:
        if debug or module.split(".")[0] in ("command", "whisper"):
            logger.info(f"Module {module} triggered")

        await task(*args)

    except Exception as e:
        exc_logger = logger.exception if debug else logger.error
        exc_logger(f"Exception in module {module} ({type(e).__name__}: {e})")
