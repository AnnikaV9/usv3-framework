#
#  Simple dice roll module.
#

import random

class Module:
    async def run(bot, text, sender, trip, ulevel):
        await bot.send(text=f"/me : *@{sender} rolls a dice and gets {random.randint(1, 6)}*")
