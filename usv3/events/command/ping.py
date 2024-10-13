#
#  Command for measuring server response time.
#

class Module:
    """
    desc: 'Measures server response time'
    """

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        pong = await bot.ws.ping()
        latency = await pong
        await bot.reply(sender, f"{round(latency * 1000)} ms")
