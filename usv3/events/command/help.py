#
#  Shows help for commands, dynamically generated from the
#  command map. Hide credits if specified in the config.
#

class Module:
    description = "Displays information about available commands."
    usage = "[command]"
    alias = "h"

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
        args = text.split()
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

        if len(args) == 1:
            await bot.reply(sender, f"""\n\\-
Chat commands: {', '.join(commands['command'])}
\\-
Whisper commands: {', '.join(commands['whisper'])}
\\-
Run {bot.prefix}help <command> [whisper] for more information about a specific command.
\\-
{"https://github.com/AnnikaV9/usv3-framework" if not bot.cmd_config['help']['hide_credits'] else ''}""")

        else:
            command = args[1]
            whisper_help = False
            event = "command"
            if len(args) > 2 and args[2] == "whisper":
                commands["command"] = commands["whisper"]
                whisper_help = True
                event = "whisper"

            if command in commands["command"]:
                desc = bot.cmd_map[event][command].get("description", "Command has no description.")
                usage = bot.cmd_map[event][command].get("usage", "")
                await bot.reply(sender, f"`{command}`\n\\-\n{desc}\n\\-\nUsage: {bot.prefix if not whisper_help else ''}{command} {usage}")

            else:
                await bot.reply(sender, f"No such command: {command}")
