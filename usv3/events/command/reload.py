#
#  Admin only command to reload the config and all modules.
#  To do this secretly, use the whisper.reload module instead.
#

import usv3.loader

class Module:
    description = "Reloads config and all modules"
    admin_only = True

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
        await bot.reply(sender, f"Reloaded config and {usv3.loader.load(bot, reload=True)} modules")
