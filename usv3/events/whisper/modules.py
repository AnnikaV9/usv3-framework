#
#  Admin only command to list all loaded modules. Unlike
#  command.modules, this replies with a whisper,
#  preventing other users from knowing what modules are
#  loaded.
#

class Module:
    description = "Lists all loaded modules"
    admin_only = True

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
        modules = []
        for event in bot.cmd_map:
            for name in bot.cmd_map[event]:
                modules.append(f"{event}.{name}")

        await bot.whisper(sender, f"\\-\nLoaded modules: {', '.join(modules)}")
