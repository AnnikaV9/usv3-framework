#
#  Allows users to mark themselves as AFK, with an optional
#  reason. Works in hand with the message.afk_check module.
#

class Module:
    description = "Marks yourself AFK (Away From Keyboard)"
    usage = "[reason]"

    @staticmethod
    def on_load(bot, namespace):
        namespace.afk_users = {}

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
        if sender not in namespace.afk_users:
            reason = None
            if args:
                reason = " ".join(args)

            namespace.afk_users[sender] = {"reason": reason, "whisper": False}
            await bot.reply(sender, f"You're now marked AFK {f'({reason})' if reason else ''}")
