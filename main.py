import traceback
import asyncio
import uvloop
import usv3.bot

if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        bot = usv3.bot.Bot()
        asyncio.run(bot.main())

    except KeyboardInterrupt:
        raise SystemExit

    except:
        traceback.print_exc()
        raise SystemExit
