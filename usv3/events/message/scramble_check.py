#
#  Checks if command.scramble's solution is in the message
#  and if so, announces the solver and the word.
#

class Module:
    @staticmethod
    async def run(bot, text, sender, trip):
        if bot.scrambled_word and bot.scrambled_word.lower() in text.lower():
            await bot.send(text=f"**@{sender}** solved the scramble! The word was: {bot.scrambled_word}")
            bot.scrambled_word = None
