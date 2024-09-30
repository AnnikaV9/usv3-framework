#
#  Allows users to mark themselves as AFK silently, with an
#  optional reason. Works in hand with the message.afk_check
#  module.
#

class Module:
    description = "Marks yourself AFK (Away From Keyboard)"
    usage = "[reason]"

    @staticmethod
    async def run(bot, namespace, text, args, sender, tripcode, ulevel) -> None:
        if sender not in bot.namespaces.command.afk.afk_users:
            reason = None
            if args:
                reason = " ".join(args)

            bot.namespaces.command.afk.afk_users[sender] = {"reason": reason, "whisper": True}
            await bot.whisper(sender, f"You're now marked AFK {f'({reason})' if reason else ''}")
