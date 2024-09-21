class Module:
    def on_load(bot):
        bot.afk_users = {}

    async def run(bot, text, sender, tripcode, ulevel):
        if sender not in bot.afk_users:
            args = text.split()
            if len(args) == 1:
                bot.afk_users[sender] = {"reason": None, "whisper": False}
                await bot.send(text=f"**@{sender}** You're now marked AFK")

            else:
                args.pop(0)
                reason = " ".join(args)
                bot.afk_users[sender] = {"reason": reason, "whisper": False}
                await bot.send(text=f"**@{sender}** You're now marked AFK ({reason})")
