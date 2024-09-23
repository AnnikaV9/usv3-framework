#
#  Lists all commands that have aliases.
#

class Module:
    description = "Lists all commands that have aliases"

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
        aliases = {}
        for command in bot.cmd_map["command"]:
            if "alias" in bot.cmd_map["command"][command]:
                aliases[command] = bot.cmd_map["command"][command]["alias"]

        alias_text = f"\n\\-\n"
        for command in aliases:
            alias_text += f"{command} - {aliases[command]}\n"

        await bot.reply(sender, alias_text)
