#
#  Admin only command to list all loaded modules. To do this
#  secretly, use the whisper.modules module instead.
#

class Module:
    """
    desc: 'Lists all loaded modules'
    groups: ['admins']
    """

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        modules = []
        for event in bot.cmd_map:
            for name in bot.cmd_map[event]:
                modules.append(f"{event}.{name}")

        await bot.reply(sender, f"Loaded modules: {', '.join(modules)}")
