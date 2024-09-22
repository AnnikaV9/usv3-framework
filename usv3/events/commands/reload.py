import usv3.loader

class Module:
    async def run(bot, text, sender, trip, ulevel):
        if trip not in bot.admins:
            await bot.send(text=f"**@{sender}** You don't have permission to use this command")
            return

        await bot.send(text=f"**@{sender}** Reloaded config and {usv3.loader.load(bot, reload=True)} modules")
