#
#  Shows help for commands, dynamically generated from the
#  command map. Hide credits if specified in the config.
#

class Module:
    description = "Displays information about available commands."
    usage = "[command] [whisper]"
    max_args = 2
    alias = "h"

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        commands = {"command": [], "whisper": []}
        groups = []
        for group in bot.groups:
            if trip in bot.groups[group]:
                groups.append(group)

        for event in ("command", "whisper"):
            for command in bot.cmd_map[event]:
                if "groups" in bot.cmd_map[event][command]:
                    if any(group in bot.cmd_map[event][command]["groups"] for group in groups):
                        commands[event].append(command)

                else:
                    commands[event].append(command)

        if not args:
            await bot.reply(sender, f"""\n\\-
Chat commands: {', '.join(commands['command'])}
\\-
Whisper commands: {', '.join(commands['whisper'])}
\\-
Run {bot.prefix}help <command> [whisper] for more information about a specific command.
\\-
{bot.cmd_config['command']['help'].get('footer', '')}""")
            return

        command = args[0]
        whisper_help = False
        event = "command"
        if len(args) > 1 and args[1] == "whisper":
            commands["command"] = commands["whisper"]
            whisper_help = True
            event = "whisper"

        if command in commands["command"]:
            desc = bot.cmd_map[event][command].get("description", "Command has no description.")
            usage = bot.cmd_map[event][command].get("usage", "")
            await bot.reply(sender, f"""`{command}`\n\\-\n{desc}\n\\-\nUsage: {f"/w {bot.config['nick']} {command}" if whisper_help else f"{bot.prefix}{command}"} {usage}""")
            return

        await bot.reply(sender, f"No such command: {command}")
