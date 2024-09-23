#
#  Admin only command to list all loaded modules. To do this
#  secretly, use the whisper.modules module instead.
#

import usv3.loader

class Module:
    description = "Lists all loaded modules"
    admin_only = True

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
        modules = []
        for event in bot.cmd_map:
            for name in bot.cmd_map[event]:
                modules.append(f"{event}.{name}")

        await bot.reply(sender, f"Loaded modules: {', '.join(modules)}")
