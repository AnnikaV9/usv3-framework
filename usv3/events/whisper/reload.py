#
#  Admin only whisper command to reload the config and all
#  modules. Unlike command.reload, this replies with a
#  whisper, preventing other users from knowing that the
#  bot was reloaded.
#

import usv3.loader


class Module:
    """
    desc: 'Lists all loaded modules'
    groups: ['admins']
    """

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        succeeded, failed = usv3.loader.load(bot, reload=True)
        await bot.whisper(sender, f"Reloaded config and modules ({succeeded} succeeded, {failed} failed)")
