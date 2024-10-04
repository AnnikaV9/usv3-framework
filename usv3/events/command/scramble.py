#
#  Sets a scrambled word for users to solve. Works in hand
#  with the message.scramble_check module.
#

import random


class Module:
    description = "Sets a scrambled word for users to solve"

    @staticmethod
    def on_load(bot, namespace):
        namespace.solution = None
        with open("assets/words.txt", "r") as wordlist:
            namespace.wordlist = wordlist.read().splitlines()

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        word = random.choice(namespace.wordlist)
        scrambled_word = "".join(random.sample(word, len(word)))
        namespace.solution = word
        await bot.send(text=f"**Scramble started:** {scrambled_word}")
