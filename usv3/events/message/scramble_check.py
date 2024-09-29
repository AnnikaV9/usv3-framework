#
#  Checks if command.scramble's solution is in the message
#  and if so, announces the solver and the word.
#

class Module:
    @staticmethod
    async def run(bot, namespace, text, sender, trip, ulevel):
        solution = bot.namespaces.command.scramble.solution
        if solution and solution.lower() in text.lower():
            await bot.send(text=f"**@{sender}** solved the scramble! The word was: {solution}")
            bot.namespaces.command.scramble.solution = None
