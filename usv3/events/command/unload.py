#
#  Admin only command to unload a module. To do this
#  secretly, use the whisper.unload module instead.
#

import usv3.loader


class Module:
    description = "Unloads modules"
    usage = "<event.name> [event.name] [ev..."
    groups = ["admins"]

    @staticmethod
    async def run(bot, namespace, text, sender, trip, ulevel):
        args = text.split()
        if len(args) == 1:
            await bot.reply(sender, f"Usage: {args[0]} {Module.usage}")
            return

        args.pop(0)
        modules_to_unload = []
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

            modules_to_unload.append(f"{event}.{name}")

        usv3.loader.unload(bot, modules_to_unload)
        await bot.reply(sender, f"Unloaded {', '.join(modules_to_unload)}")
