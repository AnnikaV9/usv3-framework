#
#  Lists all commands that have aliases.
#

class Module:
    """
    desc: 'Lists all commands that have aliases'
    """

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        aliases = {}
        for command in bot.cmd_map["command"]:
            if "alias" in bot.cmd_map["command"][command]:
                aliases[command] = bot.cmd_map["command"][command]["alias"]

        alias_text = "\n\\-\n"
        for command in aliases:
            alias_text += f"{command} - {aliases[command]}\n"

        await bot.reply(sender, alias_text)
