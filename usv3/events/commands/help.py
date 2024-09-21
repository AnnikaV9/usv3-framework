class Module:
    async def run(bot, text, sender, tripcode, ulevel):
        args = text.split()
        commands = bot.cmd_map["command"]
        if len(args) == 1:
            await bot.send(text=f"**@{sender}**\n\\-\nPrefix: {bot.config['prefix']}\n\\-\nCommands: {', '.join(commands.keys())}\n\\-\nRun .help <command> for more information about a specific command.\n\\-\nhttps://github.com/AnnikaV9/usv3")

        else:
            command = args[1]
            if command in commands.keys():
                await bot.send(text=f"**@{sender}** `{command}`\n\\-\n{commands[command]["desc"]}")

            else:
                await bot.send(text=f"**@{sender}** No such command: {command}")
