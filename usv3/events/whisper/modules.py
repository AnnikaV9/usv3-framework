#
#  Admin only command to list all loaded modules. Unlike
#  command.modules, this replies with a whisper,
#  preventing other users from knowing what modules are
#  loaded.
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

        await bot.whisper(sender, f"Loaded modules: {', '.join(modules)}")
