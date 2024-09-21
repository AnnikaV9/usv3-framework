class Module:
    async def run(bot, text, sender, tripcode):
        if bot.scrambled_word and bot.scrambled_word.lower() in text.lower():
            await bot.send(text=f"**@{sender}** solved the scramble! The word was: {bot.scrambled_word}")
            bot.scrambled_word = None
