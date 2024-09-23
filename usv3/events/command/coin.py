#
#  Simple coin flip module.
#

import random

class Module:
    description = "Flips a coin"

    async def run(bot, text, sender, trip, ulevel):
        flip =  random.randint(1, 2)
        await bot.send(cmd="emote", text=f" : *@{sender} flips a coin and gets {'heads' if flip == 1 else 'tails'}*")
