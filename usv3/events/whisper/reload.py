import usv3.loader

class Module:
    async def run(bot, text, sender, tripcode):
        if tripcode not in bot.admins:
            await bot.send(text=f"/whisper @{sender} You don't have permission to use this command")
            return

        await bot.send(text=f"/whisper @{sender} Reloaded {usv3.loader.load(bot, reload=True)} modules")
