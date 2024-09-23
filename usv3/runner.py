#
#  Runner task for catching and logging module exceptions.
#

from loguru import logger

async def run(task, module, *args):
    try:
        logger.info(f"Module {module} triggered")
        await task(*args)

    except Exception as e:
        logger.error(f"Exception in module {module}: {e}")
