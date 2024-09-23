#
#  Shows help for commands, dynamically generated from the
#  command map. Hide credits if specified in the config.
#

class Module:
    description = "Displays information about available commands."
    usage = "[command]"
    alias = "h"

    async def run(bot, text, sender, trip, ulevel):
        args = text.split()
        commands = bot.cmd_map["command"]
        if len(args) == 1:
            await bot.reply(sender, f"""\n\\-
Prefix: {bot.config['prefix']}
\\-
Commands: {', '.join(commands.keys())}
\\-
Run .help <command> for more information about a specific command.
\\-
{"https://github.com/AnnikaV9/usv3-framework" if not bot.cmd_config['help']['hide_credits'] else ''}""")

        else:
            command = args[1]
            if command in commands.keys():
                desc = commands[command].get("description", "Command has no description.")
                usage = commands[command].get("usage", "")
                admin_only = commands[command].get("admin_only", False)
                await bot.reply(sender, f"`{command}`\n\\-\n{'(Admin only) ' if admin_only else ''}{desc}\n\\-\nUsage: {bot.config['prefix']}{command} {usage}")

            else:
                await bot.reply(sender, f"No such command: {command}")
