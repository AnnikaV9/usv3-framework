#
#  Sets a scrambled word for users to solve. Works in hand
#  with the message.scramble_check module.
#

import random


class Module:
    description = "Sets a scrambled word for users to solve"

    @staticmethod
    def on_load(bot):
        bot.scrambled_word = None
        with open("assets/words.txt", "r") as wordlist:
            bot.words = wordlist.read()

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
        word = random.choice(bot.words.splitlines())
        scrambled_word = "".join(random.sample(word, len(word)))
        bot.scrambled_word = word
        await bot.send(text=f"**Scramble started:** {scrambled_word}")
