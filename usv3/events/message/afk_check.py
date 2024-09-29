#
#  Unmarks a user as AFK if they send a message. If another
#  user mentions an AFK user, it will notify the user who
#  mentioned them about their AFK status.
#

class Module:
    @staticmethod
    async def run(bot, namespace, text, sender, trip, ulevel):
        afk_users = bot.namespaces.command.afk.afk_users
        if sender in afk_users:
            if afk_users[sender]["whisper"]:
                await bot.whisper(sender, "You're no longer marked AFK")

            else:
                await bot.reply(sender, "You're no longer marked AFK")

            afk_users.pop(sender)
            bot.namespaces.command.afk.afk_users = afk_users
            return

        for user in afk_users:
            if f"@{user}" in text.split():
                reason = afk_users[user]["reason"]
                await bot.reply(sender, f"""{user} is currently AFK{f" ({reason})" if reason else ""}""")
