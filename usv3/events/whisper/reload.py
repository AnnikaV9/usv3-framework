#
#  Admin only whisper command to reload the config and all
#  modules. Unlike command.reload, this replies with a
#  whisper, preventing other users from knowing that the
#  bot was reloaded.
#

import usv3.loader

class Module:
    async def run(bot, text, sender, trip, ulevel):
        if trip not in bot.admins:
            await bot.send(text=f"/whisper @{sender} You don't have permission to use this command")
            return

        await bot.send(text=f"/whisper @{sender} Reloaded config and {usv3.loader.load(bot, reload=True)} modules")
