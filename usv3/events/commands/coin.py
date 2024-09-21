import random

class Module:
    async def run(bot, text, sender, tripcode, ulevel):
        flip =  random.randint(1, 2)
        await bot.send(text=f"/me : *@{sender} flips a coin and gets {'heads' if flip == 1 else 'tails'}*")
