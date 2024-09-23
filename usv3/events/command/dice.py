#
#  Simple dice roll module.
#

import random

class Module:
    description = "Rolls a dice"

    async def run(bot, text, sender, trip, ulevel):
        await bot.send(cmd="emote", text=f" : *@{sender} rolls a dice and gets {random.randint(1, 6)}*")
