#
#  Admin only command to reload the config and all modules.
#  To do this secretly, use the whisper.reload module instead.
#

import usv3.loader


class Module:
    """
    desc: 'Reloads config and all modules'
    groups: ['admins']
    """

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        succeeded, failed = usv3.loader.load(bot, reload=True)
        await bot.reply(sender, f"Reloaded config and modules ({succeeded} succeeded, {failed} failed)")
