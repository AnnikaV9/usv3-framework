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
        commands = ({command: bot.cmd_map["command"][command] for command in bot.cmd_map["command"] if not bot.cmd_map["command"][command].get("admin_only", False)}
                    if trip not in bot.admins else bot.cmd_map["command"])
        whisper_commands = ({command: bot.cmd_map["whisper"][command] for command in bot.cmd_map["whisper"] if not bot.cmd_map["whisper"][command].get("admin_only", False)}
                            if trip not in bot.admins else bot.cmd_map["whisper"])
        if len(args) == 1:
            await bot.reply(sender, f"""\n\\-
Prefix: {bot.config['prefix']}
\\-
Chat commands: {', '.join(commands.keys())}
\\-
Whisper commands: {', '.join(whisper_commands.keys())}
\\-
Run .help <command> [whisper] for more information about a specific command.
\\-
{"https://github.com/AnnikaV9/usv3-framework" if not bot.cmd_config['help']['hide_credits'] else ''}""")

        else:
            command = args[1]
            whisper_help = False
            if len(args) > 2 and args[2] == "whisper":
                commands = whisper_commands
                whisper_help = True

            if command in commands.keys():
                desc = commands[command].get("description", "Command has no description.")
                usage = commands[command].get("usage", "")
                admin_only = commands[command].get("admin_only", False)
                await bot.reply(sender, f"`{command}`\n\\-\n{'(Admin only) ' if admin_only else ''}{desc}\n\\-\nUsage: {bot.config['prefix'] if not whisper_help else ''}{command} {usage}")

            else:
                await bot.reply(sender, f"No such command: {command}")
