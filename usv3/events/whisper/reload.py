#
#  Admin only whisper command to reload the config and all
#  modules. Unlike command.reload, this replies with a
#  whisper, preventing other users from knowing that the
#  bot was reloaded.
#

import usv3.loader

class Module:
    admin_only = True

    async def run(bot, text, sender, trip, ulevel):
        await bot.send(cmd="whisper", nick=sender, text=f"Reloaded config and {usv3.loader.load(bot, reload=True)} modules")
