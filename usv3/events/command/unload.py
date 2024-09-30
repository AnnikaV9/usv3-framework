#
#  Admin only command to unload a module. To do this
#  secretly, use the whisper.unload module instead.
#

import usv3.loader


class Module:
    description = "Unloads modules"
    usage = "<event.name> [event.name] [ev..."
    min_args = 1
    groups = ["admins"]

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        unload_modules = []
        for module in args:
            try:
                event, name = module.split(".")

            except ValueError:
                await bot.reply(sender, f"Invalid module name format {module}, should be event.name")
                return

            if event not in bot.cmd_map:
                await bot.reply(sender, f"{event} is not a valid event")
                return

            if name not in bot.cmd_map[event]:
                await bot.reply(sender, f"Module {event}.{name} is not loaded")
                return

            unload_modules.append(f"{event}.{name}")

        usv3.loader.unload(bot, unload_modules)
        await bot.reply(sender, f"Unloaded {', '.join(unload_modules)}")
