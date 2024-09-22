class Module:
    async def run(bot, text, sender, trip):
        if sender in bot.afk_users:
            if bot.afk_users[sender]["whisper"]:
                await bot.send(text=f"/whisper {sender} -\nYou're no longer marked AFK")

            else:
                await bot.send(text=f"**@{sender}** You're no longer marked AFK")

            bot.afk_users.pop(sender)
            return

        for user in bot.afk_users:
            if f"@{user}" in text.split():
                reason = bot.afk_users[user]["reason"]
                await bot.send(text=f"""**@{sender}** {user} is currently AFK{f" ({bot.afk_users[user]['reason']})" if reason else ""}""")
