#
#  Lists all commands that have aliases.
#

class Module:
    async def run(bot, text, sender, trip, ulevel):
        aliases = {}
        for command in bot.cmd_map["command"]:
            if "alias" in bot.cmd_map["command"][command]:
                aliases[command] = bot.cmd_map["command"][command]["alias"]

        alias_text = f"**@{sender}**\n\\-\n"
        for command in aliases:
            alias_text += f"{command} - {aliases[command]}\n"

        await bot.send(text=alias_text)
