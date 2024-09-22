import random

class Module:
    def on_load(bot):
        bot.scrambled_word = None
        with open("assets/words.txt", "r") as wordlist:
            bot.words = wordlist.read()

    async def run(bot, text, sender, trip, ulevel):
        word = random.choice(bot.words.splitlines())
        scrambled_word = "".join(random.sample(word, len(word)))
        bot.scrambled_word = word
        await bot.send(text=f"**Scramble requested:** {scrambled_word}")
