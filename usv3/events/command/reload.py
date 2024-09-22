#
#  Admin only command to reload the config and all modules.
#  This sends a public message to chat with the number of
#  modules loaded. If this is not desired, use the
#  whisper.reload module instead.
#

import usv3.loader

class Module:
    async def run(bot, text, sender, trip, ulevel):
        if trip not in bot.admins:
            await bot.send(text=f"**@{sender}** You don't have permission to use this command")
            return

        await bot.send(text=f"**@{sender}** Reloaded config and {usv3.loader.load(bot, reload=True)} modules")
