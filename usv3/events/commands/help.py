class Module:
    async def run(bot, text, sender, tripcode, ulevel):
        args = text.split()
        commands = bot.cmd_map["command"]
        if len(args) == 1:
            await bot.send(text=f"""**@{sender}**
\\-
Prefix: {bot.config['prefix']}
\\-
Commands: {', '.join(commands.keys())}
\\-
Run .help <command> for more information about a specific command.
\\-
{"https://github.com/AnnikaV9/usv3-framework" if not bot.config['hide_credits'] else ''}""")


        else:
            command = args[1]
            if command in commands.keys():
                await bot.send(text=f"**@{sender}** `{command}`\n\\-\n{commands[command]['desc']}")

            else:
                await bot.send(text=f"**@{sender}** No such command: {command}")
