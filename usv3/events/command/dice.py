#
#  Simple dice roll module.
#

import random


class Module:
    description = "Rolls a dice"

    @staticmethod
    async def run(bot, namespace, text, sender, trip, ulevel):
        await bot.send(cmd="emote", text=f" : *@{sender} rolls a dice and gets {random.randint(1, 6)}*")
