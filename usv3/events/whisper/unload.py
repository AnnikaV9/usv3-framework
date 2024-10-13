#
#  Admin only command to unload a module. Unlike
#  command.unload, this replies with a whisper,
#  preventing other users from knowing that a module
#  was unloaded.
#

import usv3.loader


class Module:
    """
    desc: 'Unloads modules'
    usage: '<event.name> [event.name] [event.name] ...'
    min_args: 1
    groups: ['admins']
    """

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        unload_modules = []
        for module in args:
            try:
                event, name = module.split(".")

            except ValueError:
                await bot.whisper(sender, f"Invalid module name format {module}, should be event.name")
                return

            if event not in bot.cmd_map:
                await bot.whisper(sender, f"{event} is not a valid event")
                return

            if name not in bot.cmd_map[event]:
                await bot.whisper(sender, f"Module {event}.{name} is not loaded")
                return

            unload_modules.append(f"{event}.{name}")

        usv3.loader.unload(bot, unload_modules)
        await bot.whisper(sender, f"Unloaded {', '.join(unload_modules)}")
